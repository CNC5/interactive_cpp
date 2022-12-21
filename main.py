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
        self.main = ''
        self.types = ['int', 'string', 'void', 'float']

    def compile(self):
        assembled_file = self.includes+'\n'+self.functions+'\nint main(){\n'+self.vars+'\n'+self.main+'\nreturn 0;\n}'
        if self.args.debug:
            print(assembled_file)
        with open('tmp.cpp', 'w') as file:
            file.write(assembled_file)
        filename = str(uuid.uuid4())
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

    def include(self, name):
        self.includes += f'#include {name}\n'

    def validate(self, line):
        replace_count = 0
        if line[-1] != ';':
            if '(' in line:
                if line.split('(')[0] in self.functions_dict:
                    line += ';'
                else:
                    return line
            elif 'cout' in line:
                line += ';'
            elif line.split(' ')[0] in self.types:
                line += ';'
        return line

    def exec_line(self, line):
        first_word = line.split(' ')[0]
        if not line:
            print('execution complete, exiting')
            exit()
        if self.func_level:
            if '}' in line:
                self.func_level -= 1
                self.functions += '}\n'
            else:
                self.functions += self.validate(line)
            return
        elif first_word in self.types:
            if '{' in line:
                self.func_level += 1
                self.functions += line
                self.functions_dict.append(line.split(' ')[1].split('(')[0])
                return
            else:
                self.vars += f'{self.validate(line)}\n'
                return
        elif first_word == '#include':
            self.includes += line
            return
        else:
            self.main += self.validate(line)+'\n'
        self.compile()
        self.main=self.main.split(line)[0]


icpp = interactive_compiler()

if __name__ == '__main__':
    default_prompt = '>>> '
    function_prompt = '... '
    while True:
        if icpp.func_level > 0:
            icpp.exec_line(input(function_prompt))
        else:
            icpp.exec_line(input(default_prompt))

