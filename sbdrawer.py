import numpy as np
from PIL import Image, ImageEnhance

# RGBA np array to PIL img
def np2pil(arr):
  return Image.fromarray(arr, 'RGBA')

# PIL img to RGBA np array
def pil2np(im):
  return np.array(im, dtype='uint8')

# create rgba np array of specified color
def rgba_array(rows, cols, color=[255, 255, 255, 255]):
  img = np.zeros((rows, cols, 4), dtype='uint8')
  img[:] = color
  return img

# axis-aligned line drawer (w/ variable thickness)
def draw_axis_line(img, r1, c1, r2, c2, t, color=[0, 0, 0, 255]):
  delta = t // 2
  img[r1 - delta:r2 + t - delta, c1 - delta:c2 + t - delta] = color

# non-axis-aligned (thin) line drawer
def draw_line(img, r1, c1, r2, c2, color=[0, 0, 0, 255]):
  c1, c2, r1, r2 = int(c1), int(c2), int(r1), int(r2)
  steep = abs(c2 - c1) > abs(r2 - r1)
  if steep: c1, c2, r1, r2 = r1, r2, c1, c2
  dc, dr = c2 - c1, r2 - r1
  for r in range(r1, r2 + np.sign(dr), np.sign(dr)):
    c = round(c1 + dc * (r - r1) / dr)
    img[(c, r) if steep else (r, c)] = color

# compute star img
def compute_star_img(cell_w, bg_col=[255, 255, 255, 255]):
  img_w = 4 * cell_w
  r1, r2 = 0.14 * img_w, 0.27 * img_w
  img = rgba_array(img_w, img_w, bg_col)
  # draw outline
  for i in range(10):
    r1, r2 = r2, r1
    draw_line(img, 
      img_w / 2 - r1 * np.sin(np.pi * (0.5 + i / 5)),
      img_w / 2 + r1 * np.cos(np.pi * (0.5 + i / 5)),
      img_w / 2 - r2 * np.sin(np.pi * (0.5 + (i + 1) / 5)),
      img_w / 2 + r2 * np.cos(np.pi * (0.5 + (i + 1) / 5)))
  # floodfill
  star = np.ones((img_w, img_w), dtype=bool)
  star[0, 0] = False; frontier = [[0, 0]]
  while len(frontier) > 0:
    r, c = frontier.pop(0)
    for dr in range(-1, 2):
      for dc in range(-1, 2):
        if ((dr == 0 or dc == 0) and dr != dc and
        r + dr >= 0 and r + dr < img_w and c + dc >= 0 and c + dc < img_w and
        star[r + dr, c + dc] and (img[r + dr, c + dc] == bg_col).all()):
          star[r + dr, c + dc] = False
          frontier.append([r + dr, c + dc])
  img[star] = [0, 0, 0, 255]
  return pil2np(np2pil(img).resize((cell_w, cell_w), Image.LANCZOS))

# compute x img
def compute_x_img(cell_w, bg_col=[255, 255, 255, 255], color=[255, 0, 0, 255]):
  img = rgba_array(cell_w, cell_w, bg_col)
  p = round(0.35 * cell_w)
  draw_line(img, p, p, cell_w - p - 1, cell_w - p - 1, color)
  draw_line(img, p + 1, p, cell_w - p - 1, cell_w - p - 2, color)
  draw_line(img, p, p + 1, cell_w - p - 2, cell_w - p - 1, color)
  draw_line(img, p, cell_w - p - 1, cell_w - p - 1, p, color)
  draw_line(img, p + 1, cell_w - p - 1, cell_w - p - 1, p + 1, color)
  draw_line(img, p, cell_w - p - 2, cell_w - p - 2, p, color)
  return img

# sb drawer class
class StarBattleDrawer:
  def __init__(self,
      cell_w=33,
      border_w=3,
      cell_color=[255, 255, 255, 255],
      line_color=[0, 0, 0, 255],
      out_bg_color=[0, 0, 0, 0],
      out_cell_color=[0, 0, 0, 0]):

    self._cell_w = cell_w
    self._border_w = border_w
    self._cell_color = cell_color
    self._line_color = line_color
    self._out_bg_color = out_bg_color
    self._out_cell_color = out_cell_color

    self._cell_imgs = {
      '*': compute_star_img(cell_w, self._cell_color),
      '_*': compute_star_img(cell_w, self._out_cell_color),
      'x': compute_x_img(cell_w, self._cell_color),
      '_x': compute_x_img(cell_w, self._out_cell_color),
      'r': [255, 128, 128, 255],
      'g': [128, 255, 128, 255],
      'b': [128, 191, 255, 255],
      'y': [255, 255, 191, 255],
      'o': [255, 191, 128, 255],
      'p': [191, 128, 255, 255],
      'e': [128, 128, 128, 255],
      'k': [0, 0, 0, 255],
    }

  def cell_walls(self, r, c):
    cell_left = self._border_w // 2 + 1 + c * (self._cell_w + 1)
    cell_right = cell_left + self._cell_w - 1
    cell_top = self._border_w // 2 + 1 + r * (self._cell_w + 1)
    cell_bot = cell_top + self._cell_w - 1
    return cell_left, cell_right, cell_top, cell_bot

  def draw(self, out_file, regions_str, marks_str=''):
    # parse strings
    board = regions_str.replace('.', ' ').split('\n')
    board = [list(row) for r, row in enumerate(board) 
      if len(row) > 0 or (r != 0 and r != len(board) - 1)]
    marks = marks_str.replace('.', ' ').split('\n')
    marks = [list(row) for r, row in enumerate(marks) 
      if len(row) > 0 or (r != 0 and r != len(marks) - 1)]

    # board dims
    n_rows = len(board)
    n_cols = max([len(row) for row in board])

    # rectangularize
    for r in range(len(board)):
      board[r] += [' '] * (n_cols - len(board[r]))
      if r >= len(marks): marks.append([])
      marks[r] += [' '] * (n_cols - len(marks[r]))

    # useful vals
    img_width = n_cols * self._cell_w + n_cols + 1 + self._border_w - 1
    img_height = n_rows * self._cell_w + n_rows + 1 + self._border_w - 1

    # board img
    img = rgba_array(img_height, img_width, self._out_bg_color)

    # draw board marks
    for r in range(n_rows):
      for c in range(n_cols):
        cell_left, cell_right, cell_top, cell_bot = self.cell_walls(r, c)
        img[cell_top:cell_bot + 1, cell_left:cell_right + 1] = (
          self._out_cell_color if board[r][c] == ' ' and marks[r][c] == ' ' else
          self._cell_imgs['_' + marks[r][c]] if board[r][c] == ' ' and '_' + marks[r][c] in self._cell_imgs else
          self._cell_imgs[marks[r][c]] if marks[r][c] in self._cell_imgs else
          self._cell_color
          )

    # draw board regions
    for r in range(n_rows):
      for c in range(n_cols):
        if board[r][c] == ' ':
          continue
        cell_left, cell_right, cell_top, cell_bot = self.cell_walls(r, c)
        # draw lines
        draw_axis_line(img, cell_top - 1, cell_left - 1, cell_top - 1, cell_right + 1, 
          self._border_w if r == 0 or board[r - 1][c] != board[r][c] else 1,
          self._line_color)
        draw_axis_line(img, cell_bot + 1, cell_left - 1, cell_bot + 1, cell_right + 1, 
          self._border_w if r == n_rows - 1 or board[r + 1][c] != board[r][c] else 1,
          self._line_color)
        draw_axis_line(img, cell_top - 1, cell_left - 1, cell_bot + 1, cell_left - 1, 
          self._border_w if c == 0 or board[r][c - 1] != board[r][c] else 1,
          self._line_color)
        draw_axis_line(img, cell_top - 1, cell_right + 1, cell_bot + 1, cell_right + 1, 
          self._border_w if c == n_cols - 1 or board[r][c + 1] != board[r][c] else 1,
          self._line_color)

    np2pil(img).save(out_file)

if __name__ == '__main__':
  # make drawer given cell and border widths (in px)
  drawer = StarBattleDrawer(
    cell_w=33, 
    border_w=4,
  )
  # draw board from region and mark string
  drawer.draw(
# output file name
out_file='test.png',
# regions, separated by character
# '.' or ' ' for cells not part of the board
regions_str="""
abcddcceef
abcddceeef
abcddceeff
abcccceeef
abcccc..ff
bbcccc..ff
bbbbbb.hhi
jjjj...hhi
jjjj...hhi
jjjj.hhhhi
""",
# cell markings (empty str for no markings)
# * (star), # (off-board star), x (x), + (off-board x),
# r (red), g (green), b (blue), y (yellow), o (orange), p (purple),
# e (grey), k (black)
marks_str="""
bx.pp.xyxx
bx.xx.yxxx
xxxggxxx*x
rx.xxx*xxx
rx...xxxox
x......xox
x.......xr
x.......xr
x.......xb
x.......xb
"""
    )