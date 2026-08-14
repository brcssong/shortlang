from compilers.pyt import python_compiler

if __name__ == '__main__':
    code = """
        b[] a true false true false;
        if !!(a[1] + ((3 << 6) * 5)) = -6
            th
                i c 4;
                f a 0 150 10
                    brk;
                ff;
            en
            el
                i a 9;
                g a 10;
            se
        ;
    """
    output_code = python_compiler.compile_to_python(code)
    print(output_code)
