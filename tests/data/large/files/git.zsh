# alias gr='goreleaser'
alias gsh='git stash'
# alias gt='git tag'
alias g:='git push -u origin master'
alias gn='git open'
alias ge='git checkout'
alias gu='git commit --amend'
alias ggf='git push -f'
alias g::='git_remote_add_origin_from_active_link'
alias g="git"
alias gi='git init'
alias gl='git pull'
alias gcl='git clone'
alias g.='git add .'
alias ga='git add'
# alias gb='git branch'
alias gbd='git branch -d'
alias gg='git push'
#alias gr='git rm'
# alias gf='git fetch'
alias glp='git pull && git push'
alias grao='git remote add origin'
alias gz='git discard'
#alias gr='git rm --cached -r'

# undo your last commit, but don't throw away your changes
alias greset='git reset --soft HEAD^'


# _diff
alias gd='git diff'
alias gds='git diff --staged'
alias gdn='git diff --name-only'

# _status
alias gs='git status --short'
alias gss='git show --word-diff=color'


alias ggn='git_add_origin_and_origin_push'


# _commit
alias gdf='git commit . -m ':tada: initial commit''
alias gpm="git push origin master"
alias gpd="git push origin develop"

# _git all add commits
alias ggm='git_commit_update'

# _utilities

# remove git from a project
alias ungit="find . -name '.git' -exec rm -rf {} \;"

# _app
alias gto='gittower'


# _list commit hashes
function commits() {
git log $1 --oneline --reverse | cut -d' ' -f 1 | tr '/n' ' '
}
