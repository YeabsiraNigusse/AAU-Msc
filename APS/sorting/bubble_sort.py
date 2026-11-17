

def bubble(list):
    n = len(list)
    for i in range(n):
        for j in range(n-1):
            if list[j] > list[j + 1]:
                temp = list[j]
                list[j] = list[j+1]
                list[j+1] = temp
    return list


print(bubble([8, 7, 9, 6, 5, 4, 4, 3, 2, 1]))



def bubble(list):
    n = len(list)

    for i in range(n):
        j = 1
        while j < n:
            if list[j-1] > list[j]:
                temp = list[j]
                list[j] = list[j-1]
                list[j-1] = temp
            j += 1

    return list


print(bubble([7, 8, 9, 6, 5, 4, 4, 3, 2, 1]))


