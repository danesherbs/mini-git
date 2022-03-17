# mini-git
A small Git-like version control system implementing the core parts of Git for educational purposes.

### Commands I currently don't understand well but want to
- Rebase
- Cherry pick
- Reset
- Branch

### Design style

I opted to write this with a [functional core and imperative shell](https://www.destroyallsoftware.com/screencasts/catalog/imperative-to-oo-to-functional). The general workflow was:
1. Re-write large functions in terms of many granular functions (1 to 2 lines)
2. Group granular functions with roughly the same arguments into a class
3. Make class methods referentially transparent i.e. keep only pure functions in the class and extract out everything else

Following this results in a functional core (the class) and an imperative shell (everything else).
