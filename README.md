Flock is a library for managing groups of lambda closures in Python.  The basic trick is to take a group of 
lambdas with no parameters and then call them if/when you need their value.  For example:

```python
>>> myList = []
>>> myList.append(lambda:5)
>>> myList.append(lambda:3)
>>> myList.append(lambda:myList[0]()+myList[1]())
>>> [x() for x in myList]
[5, 3, 8]
```

The trick is the last element.  As you can see the third lambda includes the list itself.

For Flock this is encapsulated within an implementation of dict called a FlockDict.