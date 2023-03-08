#!/usr/local/cs/bin/python3

# Keep the function signature,
# but replace its body with your implementation.
#
# Note that this is the driver function.
# Please write a well-structured implemention by creating other functions outside of this one,
# each of which has a designated purpose.
#
# As a good programming practice,
# please do not use any script-level variables that are modifiable.
# This is because those variables live on forever once the script is imported,
# and the changes to them will persist across different invocations of the imported functions.

import zlib
import pathlib
import os


class CommitNode:
    def __init__(self, commit_hash):
        """
        :type commit_hash: str
        """
        self.commit_hash = commit_hash
        self.parents = set()
        self.children = set()

    def __lt__(self, other):
        return self.commit_hash < other.commit_hash

        
# Returns an absolute path for where the git repo is located
def find_git_repo():
    cwd = pathlib.Path().cwd()
    while cwd != cwd.parent:
        if cwd.joinpath('.git').is_dir():
            return str(cwd)
        cwd = cwd.parent
        
    return -1


# Returns a dictionary mapping all branch names in the repo to their respective commit hashes 
def get_branches():
    branches = {}

    for dirname, dirs, files in os.walk(os.path.join('.', '.git', 'refs', 'heads')):
        for f in files:
            branch = os.path.join(dirname, f)
            branch_file = open(branch, 'r')
            branch_hash = branch_file.readline().strip()
            branch_name = branch[18:]
            branches[branch_name] = branch_hash

    return branches


# Returns a string representing the decompressed git object (commit) given its hash
def read_commit(hash):
    obj_file = os.path.join('.git', 'objects', hash[:2], hash[2:])
    with open(obj_file, 'rb') as f:
        data = f.read()
    decompressed_data = zlib.decompress(data)
    return decompressed_data


# Returns a graph (as a dictionary) of all the commits in the repo using the CommitNode class
def build_commit_graph(branch_tips):
    graph = {} # This is a dictionary which matches commit SHA-1 hashes to their CommitNode
    visited = set() # This contains a set of all the commit hashes that have been visited
    to_process = branch_tips # This keeps track of all commit hashes that need to be visited

    while to_process: 
        curr_hash = to_process.pop(0)
        
        if curr_hash in visited:
            continue
        visited.add(curr_hash)

        if curr_hash not in graph:
            graph[curr_hash] = CommitNode(curr_hash)

        curr_node = graph[curr_hash]
        commit_content = read_commit(curr_hash).decode().splitlines()

        for line in commit_content:
            if "parent " in line:
                parent_hash = line[7:]

                if parent_hash not in visited:
                    to_process.append(parent_hash)

                if parent_hash not in graph:
                    graph[parent_hash] = CommitNode(parent_hash)

                parent_node = graph[parent_hash]
                curr_node.parents.add(parent_node)
                parent_node.children.add(curr_node)

    return graph


# Returns the topologically-sorted version of the commit graph
# as a list of corresponding commit hashes
def sort(graph):
    sorted_commits = []

    hash_to_num_children = {}
    for key, value in graph.items():
        hash_to_num_children[key] = len(value.children)
        
    to_process = [node for node in graph.values() if not node.children]

    while to_process:
        curr = to_process.pop(0)
        sorted_commits.append(curr.commit_hash)

        for p in sorted(curr.parents):
            hash_to_num_children[p.commit_hash] = hash_to_num_children[p.commit_hash] - 1
            if hash_to_num_children[p.commit_hash] == 0:
                to_process.append(p)

    return sorted_commits


# Prints the topologically-sorted commits in format as specified by spec
def print_commits(sorted_commits, branches):
    last_visited = sorted_commits[0]

    first_output = sorted_commits[0].commit_hash
    assoc_branches_1 = [key for key, value in branches.items() if value == sorted_commits[0].commit_hash]
    assoc_branches_1.sort()
    if assoc_branches_1:
        first_output += " " + " ".join(b for b in assoc_branches_1)

    print(first_output)
        
    for commit in sorted_commits[1:]:
        if commit not in last_visited.parents:
            last_parents = " ".join(p.commit_hash for p in last_visited.parents)
            print(last_parents + "=") #insert sticky end with newline
            print()

            curr_children = " ".join(c.commit_hash for c in commit.children)
            print("=" + curr_children) #insert sticky start

        output = commit.commit_hash
        assoc_branches = [key for key, value in branches.items() if value == commit.commit_hash]
        assoc_branches.sort()
        if assoc_branches:
            output += " " + " ".join(b for b in assoc_branches)

        print(output)
        last_visited = commit
    
            
def topo_order_commits():
    # Step 1: Find the git repo and change cwd accordingly
    git_repo = find_git_repo()
    if git_repo == -1:
        print('Not inside a Git repository')
    os.chdir(git_repo)

    # Step 2: Get a dict of all branches used (maps commit hash to branch name
    branches = get_branches()

    # Step 3: Build a graph of all of the commits
    branch_tips = list(branches.values())
    commit_graph = build_commit_graph(branch_tips)
    
    # Step 4: Topological sort
    sorted_commit_hashes = sort(commit_graph)
    sorted_commits = [commit_graph[c] for c in sorted_commit_hashes]
    
    # Step 5: Print sorted order
    print_commits(sorted_commits, branches)
        
    
if __name__ == '__main__':
    topo_order_commits()



'''
Additional Notes:



'''
