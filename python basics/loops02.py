# loop example 1
# for i in range (-5,6):
#     print (i)



# loop example2
# PlayListRatings = [10, 9.5, 10, 8, 7.5, 5, 10, 10]
# for ratings in PlayListRatings:
#     if (ratings<6):
#         break
#     print(ratings)


# loop example3
# squares = ['orange', 'orange', 'purple', 'blue ', 'orange']
# new_squares = []
# i=0
# while(i<len(squares) and squares[i]=='orange'):
#     new_squares.append(squares[i])
#     i+=1
#     print(new_squares)



# loop example 4
for i in range(1,16):
    if(i%3==0):
        continue
    elif(i>12):
        break
    else:
        print(i)