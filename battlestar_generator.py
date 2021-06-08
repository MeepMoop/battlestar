import pickle
import os.path

import numpy as np
from dataclasses import dataclass

from sbdrawer import StarBattleDrawer

## backtracker to generate star configs

@dataclass
class ProblemSpecs:
  size: int
  n_stars: int
  candidates: list
  successors: list
  boards: list

def compute_candidates(size, n_stars):
  def recurse(candidates, cols=[]):
    if len(cols) == n_stars:
      candidates.append(cols)
      return
    for c in range(cols[-1] + 2 if cols else 0, size - 2 * (n_stars - len(cols) - 1)):
      recurse(candidates, cols + [c])
  candidates = []; recurse(candidates)
  return candidates

def compute_successors(candidates):
  successors = [[] for _ in range(len(candidates))]
  def compare_candidates(candidates, i, j):
    for c1 in candidates[i]:
      for c2 in candidates[j]:
        if abs(c2 - c1) <= 1:
          return False
    return True
  for i in range(len(candidates)):
    for j in range(len(candidates)):
      if compare_candidates(candidates,i, j):
        successors[i].append(j)
  return successors

def backtrack(specs, board, col_counts, successors, row):
  if row == specs.size:
    specs.boards.append(tuple(board))
    return
  for s in successors:
    cols = specs.candidates[s]
    valid = True
    for col in cols:
      if col_counts[col] == specs.n_stars:
        valid = False
        break
    if valid:
      board[row] = cols
      for col in cols:
        col_counts[col] += 1
      backtrack(specs, board, col_counts, specs.successors[s], row + 1)
      board[row] = None
      for col in cols:
        col_counts[col] -= 1

def generate_star_configs(S, N):
  candidates = compute_candidates(S, N)
  successors = compute_successors(candidates)
  specs = ProblemSpecs(
      size=S,
      n_stars=N,
      candidates=candidates,
      successors=successors,
      boards=[]
    )
  backtrack(specs, [None] * S, [0] * S, range(len(candidates)), 0)
  return specs.boards

def matrixify_star_configs(S, star_configs):
  mat = np.zeros((len(star_configs), S, S), dtype=int)
  for i, star_config in enumerate(star_configs):
    for r in range(S):
      for c in star_config[r]:
        mat[i, r, c] = 1
  return mat

## puzzle generator

def generate_puzzle(S, N, temperature, star_configs):
  while True:
    # init board
    board = np.zeros((S, S), dtype=int)
    # sample solution
    idx = np.random.randint(star_configs.shape[0])
    solution = star_configs[idx]
    mask = 1 - solution
    # copy database
    remaining_sols = np.delete(star_configs, idx, axis=0)
    # place blocks
    while remaining_sols.shape[0] > 0:
      # compute star frequencies
      star_freqs = remaining_sols.mean(0) * mask
      # generate distribution (weighted boltzmann thing)
      logits = np.exp(temperature * (star_freqs - star_freqs.max())) * star_freqs
      p = logits / logits.sum()
      # sample block
      block = np.random.choice(S * S, p=p.flatten())
      board[block // S, block % S] = 1
      # prune solutions
      remaining_sols = remaining_sols[(remaining_sols * board).sum(2).sum(1) == 0]
    # extra constraints (filter boards, etc.)
    if not ((board.sum(0) == S - N).any() or (board.sum(1) == S - N).any()):
      break
  return board, solution

if __name__ == '__main__':
  import sys

  # generator settings
  S = int(sys.argv[1])
  N = int(sys.argv[2])
  temperature = int(sys.argv[3])
  n_puzzles = int(sys.argv[4])

  # star config database
  if os.path.exists(f'star_configs_{S}_{N}.p'):
    print('> loading star configs...')
    with open(f'star_configs_{S}_{N}.p', 'rb') as file:
      star_configs = pickle.load(file)
  else:
    print('> generating star configs...')
    star_configs = generate_star_configs(S, N)
    with open(f'star_configs_{S}_{N}.p', 'wb') as file:
      pickle.dump(star_configs, file)

  # unpack star configs
  print('> processing star configs...')
  star_configs = matrixify_star_configs(S, star_configs)

  # puzzle drawer
  drawer = StarBattleDrawer(
    cell_w=33, 
    border_w=4,
    out_bg_color=[0, 0, 0, 255],
    out_cell_color=[0, 0, 0, 255]
  )

  # generate
  print('> generating...')
  for i in range(1, n_puzzles + 1):
    board, solution = generate_puzzle(S, N, temperature, star_configs)
    # output
    print('board:')
    print('\n'.join(''.join('▓▓' if board[r, c] == 1 else '░░' for c in range(S)) for r in range(S)))
    print('solution:')
    print('\n'.join(' '.join('*' if solution[r, c] == 1 else '.' for c in range(S)) for r in range(S)))
    drawer.draw(
      out_file=f'battlestar_{S}_{N}_{temperature}_{i}.png',
      regions_str='\n'.join([''.join(['.' if x == 1 else 'a' for x in board[r]]) for r in range(S)])
    )
    print(f'> saved battlestar_{S}_{N}_{temperature}_{i}.png')
