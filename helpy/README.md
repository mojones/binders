## Copy and paste into a python interpreter after running `import helpy`

Requires `colorama` for terminal colours.

### Used the wrong variable NameError

```
names = """graham chapman, eric idle,
terry gilliam, terry jones,
john cleese, michael palin"""

total_count = 0
for vowel in 'aeiou':
    single_count = names.count(vowel)
    total_count = total_count + single_count

print(tot_count)
```



### called a method on the wrong variable

```
names = open('names.txt')
for line in names:
    print(len(names.rstrip('\n')))
```


### consumed a file twice

```
names_file = open('names.txt')
names = names_file.read()
print(names) # check that it worked

for line in names_file:
    print(len(line.rstrip('\n')))
```
