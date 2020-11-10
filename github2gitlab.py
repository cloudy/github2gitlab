#!/usr/bin/env python3 

import git
import github
import gitlab
import os
import config
import argparse
import glob
import shutil


parser = argparse.ArgumentParser(description='github2gitlab')
parser.add_argument('--user', type=str, help='enter a github username',
        required=True)
args = parser.parse_args()
USER = args.user

g = github.Github(config.github_token)
gl = gitlab.Gitlab(config.gitlab_url, private_token=config.gitlab_token)

# select or create new group
groups = gl.groups.list(search=config.gitlab_group)
if len(groups) == 0:
    archive_group = gl.groups.create({'name':config.gitlab_group,
        'path':config.gitlab_group})
else:
    archive_group = groups[0]  # TODO: make sure this hits the right match

# select or create user subgroup
subgroups = archive_group.subgroups.list(search=USER)
if len(subgroups) == 0:
    user_group = gl.groups.create({'name':USER, 'path':USER, 'parent_id':archive_group.id})
else:
    user_group = subgroups[0]
r_user_group = gl.groups.get(user_group.id, lazy=True)  # wrap as group to access list of repos

# make sure repository directory is created for local clone
if not os.path.isdir(config.repo_dir + USER):
    os.makedirs(config.repo_dir + USER)

# go through github repos and clone them all, then add to gitlab instance
for repo in g.get_user(USER).get_repos():
    print(repo.name)
    repo_path = config.repo_dir + '/'.join([USER, repo.name])
    repo_url = config.github_url + '/'.join([USER, repo.name])
    readme_path = repo_path + '/README.md'
    # clone/pull code from online repository
    try:
        if os.path.isdir(repo_path):
            repo_local = git.Repo(repo_path)
            repo_local.remotes.origin.pull()
        else:
            repo_local = git.Repo.clone_from(repo_url, repo_path)
    except Exception as e:
        print('Failed to clone or git pull repository:', e)

    # add readme, or append to readme the repo info
    if config.repository_url_readme:
        try:
            for f in glob.glob(repo_path + '*'):
                if 'readme' in f.lower():
                    readme_path = f
            rdme_f = open(readme_path, 'a+')
            rdme_f.write("\n\n## Repository downloaded from: \n\n" + repo_url + "\n\n")
            rdme_f.close()
            repo_local.index.add([readme_path.split('/')[-1]])
            repo_local.git.add(update=True)
            repo_local.index.commit('Add source URL to README.')
        except Exception as e:
            print('Failed to write README.md:', e)

    # push to gitlab
    try:
        repos = r_user_group.projects.list(search=repo.name)
        if len(repos) == 0:
            gitlab_repo = gl.projects.create({'name':repo.name, 'path':repo.name,
                'namespace_id':user_group.id})
        else:
            gitlab_repo = repos[0]

        remote_url = 'https://' + config.gitlab_user + ':' + config.gitlab_token + \
                '@' + gitlab_repo.web_url[8:] + '.git'
        remote = git.remote.Remote(repo_local, config.gitlab_remote)
        if not remote.exists():
            remote = repo_local.create_remote(config.gitlab_remote, url=remote_url)
        remote.push()
    except Exception as e:
        print('Failed to push repository:',  e)

    # remove old repository
    try:
        shutil.rmtree(repo_path)
    except Exception as e:
        print('Failed to delete directory: ', e)

