ShortLang is meant to be a simply implemented, experimental programming language with basic features in the meantime.
0% of this project is or will ever be coded by AI.

Some properties:
- It's meant to flow easily, like reading with continuity (i.e. the `if/th/en/el/se` pattern)
- Keywords (i.e. `i/b/s/i[]/b[]/s[]`) take precedence over all other terms and can be shadowed, as they are always the first element in a code statement.
- Implementations of the lexer, parser, and Python compiler are supported.
- *an interesting use case* - for programs with simple logic, code it quickly in ShortLang, compile to Python, and fill in the rest of your desired functionalities

Roadmap:
- Test suite
- Custom classes
- Functions
- I/O
- Compilation into ASM

Sample program:
```
b[] a true false true false;
if !!(a[1] + ((3 << 6) * 5)) = -6
    th
        i c 4;
        f a 0 150 10
            brk;
        ff;
    en
    el
        i d 9;
        g o 10;
    se
;

[i]nteger
[b]oolean
[s]tring
i[] integer array
b[] boolean array
s[] string array

[if]
[th][en]
[el][se]

assi[g]n
assi[gn] array

[f]or begin
[ff]or end

[brk] break
[cnt] continue

+ - / * << >> | & ^ **
= <= >= < > !
&& || !!
```
