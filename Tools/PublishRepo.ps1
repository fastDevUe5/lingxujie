#requires -Version 5.1
# Publishes this repository to a new remote, either by URL or by creating the GitHub
# repository from a personal access token. Pre-flight checks run first so the push does
# not fail halfway (oversized blobs, dirty tree, missing LFS).
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File Tools\PublishRepo.ps1 -Url git@github.com:user/LingXuJie.git
#   powershell -ExecutionPolicy Bypass -File Tools\PublishRepo.ps1 -Token <pat> -Private
#   powershell -ExecutionPolicy Bypass -File Tools\PublishRepo.ps1 -DryRun     # rehearsal, no network
#
# NOTE: keep this file ASCII-only (PowerShell 5.1 reads BOM-less files as ANSI).

param(
    [string]$Url = '',
    [string]$Token = '',
    [string]$RepoName = 'LingXuJie',
    [switch]$Private,
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
Push-Location $Root
try {
    # --- pre-flight ---------------------------------------------------------
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw 'git is not on PATH' }
    if (-not (git lfs version 2>$null)) { throw 'git-lfs is not installed (git lfs version failed)' }

    $dirty = git status --porcelain
    if ($dirty) {
        Write-Host 'Working tree is not clean:' -ForegroundColor Yellow
        $dirty | ForEach-Object { Write-Host "  $_" }
        throw 'commit or stash first - the push would leave the remote without them'
    }

    $branch = (git rev-parse --abbrev-ref HEAD).Trim()
    if ($branch -ne 'main') { Write-Host "WARNING: pushing branch '$branch', not 'main'" -ForegroundColor Yellow }

    # GitHub rejects any single file over 100 MB; refuse early with a readable message.
    $big = git rev-list --objects --all |
        git cat-file --batch-check='%(objecttype) %(objectsize) %(rest)' |
        Where-Object { $_ -like 'blob*' } |
        ForEach-Object { $p = $_ -split ' '; [pscustomobject]@{ Size = [int]$p[1]; Path = ($p[2..($p.Length - 1)] -join ' ') } } |
        Where-Object { $_.Size -gt 95MB } |
        Sort-Object Size -Descending
    if ($big) {
        $big | Select-Object -First 5 | ForEach-Object { Write-Host ("  {0:N1} MB  {1}" -f ($_.Size / 1MB), $_.Path) -ForegroundColor Red }
        throw 'history contains blobs over 95 MB; rewrite history first (git filter-branch)'
    }

    $lfsCount = (git lfs ls-files | Measure-Object).Count
    Write-Host "pre-flight ok: branch=$branch, lfs files=$lfsCount"

    # --- resolve the destination -------------------------------------------
    if ($DryRun) {
        $bare = Join-Path $Root 'Saved\PublishDryRun.git'
        if (Test-Path $bare) { Remove-Item $bare -Recurse -Force }
        git init --bare $bare | Out-Null
        if ((git remote) -contains 'publish-dryrun') { git remote remove publish-dryrun }
        git remote add publish-dryrun $bare
        Write-Host "dry run -> $bare"
        git push publish-dryrun $branch
        git remote remove publish-dryrun
        Write-Host 'dry run finished (nothing left behind except a temp bare repo under Saved\)'
        return
    }

    if (-not $Url) {
        if (-not $Token) {
            throw 'need -Url <remote url> or -Token <pat> (see Docs/P0-ROADMAP.md)'
        }

        # Create the repository through the REST API, then push over SSH so the token
        # never ends up inside .git/config.
        $body = @{ name = $RepoName; private = [bool]$Private; auto_init = $false } | ConvertTo-Json
        $headers = @{
            Authorization          = "token $Token"
            Accept                 = 'application/vnd.github+json'
            'X-GitHub-Api-Version' = '2022-11-28'
            'User-Agent'           = 'LingXuJie-PublishRepo'
        }
        Write-Host "creating github repository '$RepoName' (private=$([bool]$Private)) ..."
        $repo = Invoke-RestMethod -Method Post -Uri 'https://api.github.com/user/repos' -Headers $headers -Body $body
        Write-Host "created: $($repo.html_url)"
        $Url = $repo.ssh_url
        Write-Host "pushing over ssh: $Url"
    }

    # --- push ---------------------------------------------------------------
    $existing = git remote
    if ($existing -contains 'origin') {
        git remote set-url origin $Url
    }
    else {
        git remote add origin $Url
    }

    git push -u origin $branch
    if ($LASTEXITCODE -ne 0) { throw "git push failed ($LASTEXITCODE)" }
    git lfs push --all origin $branch
    Write-Host ''
    Write-Host "done: $(git remote get-url origin)"
    git remote show origin | Select-Object -First 4
}
finally {
    Pop-Location
}
