

def insertion_sort(list):
    n = len(list)

    for i in range(1, n):
        key = list[i]

        j = i - 1

        while j >= 0 and list[j] > key:
            list[j+1] = list[j]
            j -= 1

        list[j + 1] = key

    return list

print(insertion_sort([9, 8, 7, 6]))

        