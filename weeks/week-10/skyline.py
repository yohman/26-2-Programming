# 数字は、ビルの高さ
heights = [2, 5, 3, 6, 4, 2]


def skyline_row(level):
    row = ""
    for height in heights:
        if height >= level:
            row += "[#] "
        else:
            row += "    "
    return row.rstrip()


# 高いところから1段ずつ描く
for level in range(max(heights), 0, -1):
    print(skyline_row(level))
print("=" * (4 * len(heights)))
