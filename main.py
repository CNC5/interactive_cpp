import argparse
import subprocess
import os
import uuid

class interactive_compiler:
    def __init__(self):
        parser = argparse.ArgumentParser(description='')
        parser.add_argument('-d', '--debug',
                            action='store_true',
                            help='enable debugging',
                            dest='debug',
                            default=False)
        self.args = parser.parse_args()
        self.includes = '#include <iostream>\nusing namespace std;\n'
        self.func_level = 0
        self.functions = ''
        self.functions_dict = []
        self.vars = ''
        self.vars_dict = []
        self.main = ''
        self.types = ['int', 'string', 'void', 'float']

    def compile(self):
        assembled_file = self.includes+'\n'+self.functions+'\nint main(){\n'+\
            self.vars+'\n'+self.main+'\nreturn 0;\n}'
        if self.args.debug:
            print(f'vars dict: {self.vars_dict}')
            print(f'full file:\n{assembled_file}')
        with open('tmp.cpp', 'w') as file:
            file.write(assembled_file)
        filename = str(uuid.uuid4())
        if self.args.debug:
            print('compilation stage started:')
        subprocess.run(['g++', 'tmp.cpp', '-o', filename])
        if os.name == "nt":
            name = ".\\" + filename + ".exe"
        else:
            name = "./" + filename
        if os.path.isfile(name):
            subprocess.run([name])
            subprocess.run(['rm', name])
        else:
            print('compilation failed')
        subprocess.run(['rm', 'tmp.cpp'])
        if self.args.debug:
            print('compilation stage complete')

    def include(self, name):
        self.includes += f'#include {name}\n'

    def validate(self, line):
        if line[-1] != ';':
            if line.split(' ')[0] in self.types and '(' in line:
                return line
            else:
                line += ';'

        return line

    def exec_line(self, line):
        first_word = line.split(' ')[0]
        if line == '!rst':
            self.__init__()
            print('scope reset')
            return
        elif not line:
            print('execution complete, exiting')
            exit()
        elif line in self.vars_dict:
            line = f'cout<<{line}<<endl;'
            self.main += line+'\n'
        elif self.func_level:
            if '}' in line:
                self.func_level -= 1
                self.functions += '}\n'
            else:
                self.functions += self.validate(line)
            return
        elif first_word in self.types:
            if '(' in line:
                self.func_level += 1
                self.functions += line
                self.functions_dict.append(line.split(' ')[1].split('(')[0])
                return
            else:
                var_type, var_name = line.split(' ', 1)
                var_name = var_name.split('=')[0]
                if var_name in self.vars_dict:
                    tmp = self.vars
                    self.vars = ''
                    for x in tmp.split('\n'):
                        if f' {var_name}' not in x:
                            self.vars=self.vars+x+'\n' 
                self.vars += f'{self.validate(line)}\n'
                if not var_name in self.vars_dict:
                    self.vars_dict.append(var_name)
                return
        elif first_word == '#include':
            self.includes += line
            return
        else:
            self.main += self.validate(line)+'\n'
        self.compile()
        self.main = ''

icpp = interactive_compiler()

if __name__ == '__main__':
    default_prompt = '>>> '
    function_prompt = '... '
    while True:
        if icpp.func_level > 0:
            icpp.exec_line(input(function_prompt))
        else:
            icpp.exec_line(input(default_prompt))

