# Flock 

Flock is a library for managing groups of closures in Python, most commonly zero argument lambda closures.  The basic trick is to take a group of lambdas with no parameters and then call them if/when you need their value.  For example:

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

Flock is mostly useful as a way to memorialize--however temporarily--mathematical models and then allow for execution or re-execution as you experiment with them non-linearly.

## Concepts 

* Flock is a a pragmatic library if you find it useful, use it.  Purity will not be enforced, but might be flagged or accessible via interface or sub-classes.
* 0 argument closures - a closure with 0 arguments can be executed at anytime however Python does not guarantee that this will not cause an error nor does Flock attempt to do so.  
* Flock - a set of related closures, aggregators, and flocks.  A flock represents a model or formula of some sort and pragmatically will not be changed by exterior components.
* Aggregator - an object that works across a set of closures in one or more flocks applying a common function to them.  This is like a column in Excel filled entirely with a consistent formula.
* _new_ dataset the datavalues in a flock - usage and meaning of this is currently unclear.
* _new_ ruleset the rules in a flock - everything in a flock that is not data.  Combining data and rules will restore the flock, but rules are harder to persist.