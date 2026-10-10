def mergesort(arr: list) -> list:      # O(n log n) time complexity, O(n) space complexity
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    Larr = arr[:mid]
    Rarr = arr[mid:]
    
    Larr = mergesort(Larr)
    Rarr = mergesort(Rarr)
    i = j = curr = 0
    
    while i < len(Larr) and j < len(Rarr):
        if Larr[i] <= Rarr[j]:
            arr[curr] = Larr[i]
            i += 1
        else:
            arr[curr] = Rarr[j]
            j += 1
        curr += 1
    
    while i < len(Larr):
        arr[curr] = Larr[i]
        i += 1
        curr += 1
    
    while j < len(Rarr):
        arr[curr] = Rarr[j]
        j += 1
        curr += 1
    
    return arr

def bubblesort(arr: list) -> list:     # O(n^2) time complexity, O(1) space complexity
    if len(arr) <= 1:
        return arr

    N = len(arr)
    for i in range(N):
        swap = False
        for j in range(0, N-i-1):
            if arr[j] > arr[j+1]:    
                arr[j], arr[j+1] = arr[j+1], arr[j]  # WESWAP
                swap = True
        if swap == False:
            break

    return arr

def selectionsort(arr: list) -> list:  # O(n^2) time complexity, O(1) space complexity
    # Min select
    if len(arr) <= 1:
        return arr

    N = len(arr)
    for i in range(N-1):
        minindex = i
        for j in range(i+1, N):
            if arr[j] < arr[minindex]:
                minindex = j
        arr[i], arr[minindex] = arr[minindex], arr[i]
    return arr

def insertionsort(arr: list) -> list:  # O(n^2) time complexity, O(1) space complexity
    if len(arr) <= 1:
        return arr

    N = len(arr)
    for i in range(1, N):
        key = arr[i]
        j = i - 1
        while j >= 0 and key < arr[j]:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr

def countsort(arr: list) -> list:      # O(n) time complexity, O(n + k) space complexity
    if len(arr) <= 1:
        return arr

    N = len(arr)
    count = [0] * (max(arr)+1)
    newarr = []

    for i in arr:
        count[i] += 1

    for i in range(len(count)):
        if count[i] != 0:
            var = count[i]
            while(var != 0):
                newarr.append(i)
                var -= 1
    return newarr


print(selectionsort([1,4,23,64,2,6,53]))