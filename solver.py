from time import perf_counter

import numpy as np

from problem import problem


class Solver:
    def __init__(self, problem, verbose=1):
        self.board = np.array(problem)
        self.proposals = np.ones((9, 9, 9), dtype=np.bool)
        self.verbose = verbose

        for i in range(81):
            r = i // 9
            c = i % 9
            n = self.board[r, c]
            if n:
                self.remove_proposal(r, c, n)

        if not self.check_valid(self.board, self.proposals):
            raise RuntimeError('The problem is not valid!')

    def print_board(self):
        print(self.board)

    def print_proposals(self, proposals=None):
        for i in range(81):
            r = i // 9
            c = i % 9
            print(r, c, end=' ')
            for n in range(9):
                if proposals is not None:
                    if proposals[r, c, n]:
                        print(n + 1, end=' ')
                else:
                    if self.proposals[r, c, n]:
                        print(n + 1, end=' ')
            print()

    def remove_proposal(self, r, c, n, proposals=None):
        n -= 1
        assert 0 <= n <= 8
        if proposals is None:
            proposals_ = self.proposals
        else:
            proposals_ = proposals
        proposals_[:, c, n] = 0  # clear column
        proposals_[r, :, n] = 0  # clear row
        br, bc = self.get_block_rc(r, c)
        proposals_[br * 3:br * 3 + 3, bc * 3:bc * 3 + 3, n] = 0

        proposals_[r, c, :] = 0

        if proposals is not None:
            return proposals_

    @staticmethod
    def get_block_id(r, c):
        return 3 * (r // 3) + (c % 3)

    @staticmethod
    def get_block_rc(r, c):
        c = c // 3
        r = r // 3
        return r, c

    def check_valid(self, board, proposals):
        for i in range(81):
            r = i // 9
            c = i % 9
            if (board[r, c] == 0) and (proposals[r, c].sum() == 0):
                print('Failed. (%d, %d) has no candidate!' % (r, c), end='')
                return False
        return True

    def solve(self):
        print(self._solve(self.board, self.proposals, 0))

    def _solve(self, board, proposals, depth):
        if not self.check_valid(board, proposals):
            return
        if proposals.sum() == 0:
            print('Found.')
            return board
        prefix = ' ' * depth
        # First, get the coord with min proposals
        num_proposals = proposals.sum(axis=-1)
        num_proposals[num_proposals == 0] = 99
        idx = num_proposals.argmin()
        r = idx // 9
        c = idx % 9

        possible_values = []
        for n in range(9):
            if proposals[r, c, n]:
                possible_values.append(n + 1)
        if self.verbose:
            print('\n' + prefix + 'element (%d, %d) with %d proposals' % (r, c, num_proposals[r, c]),
                  possible_values, end='')

        for possible_value in possible_values:
            print('\n' + prefix + ' trying', possible_value, '...', end='')  # TODO: verbose
            new_board = board.copy()
            new_board[r, c] = possible_value
            new_proposals = self.remove_proposal(r, c, possible_value, proposals.copy())

            solution = self._solve(new_board, new_proposals, depth + 1)

            if solution is not None:
                return solution

        # Fail to find a solution
        return


solver = Solver(problem)
tic = perf_counter()
solver.solve()
print('finished in', perf_counter() - tic)
