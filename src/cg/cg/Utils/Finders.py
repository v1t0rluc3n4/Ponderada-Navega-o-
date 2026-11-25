def find(occupancy_grid, target):
    for i, row in enumerate(occupancy_grid):
        for j, cell in enumerate(row):
            if cell == target:
                return i, j

def is_obstructed(occupancy_grid, pos):
    row, col = pos
    if not (0 <= row < len(occupancy_grid) and
            0 <= col < len(occupancy_grid[0])):
        return True
    return occupancy_grid[row][col] == 'b'
