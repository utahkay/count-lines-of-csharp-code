from pathlib import PureWindowsPath
from pathlib import PurePath
import re

#
# Count lines of C# code in a Visual Studio solution file
# 

class CountLinesOfCode:
    def __init__(self):
        self.unable_to_parse = list()
        self.number_of_files = 0
        self.number_of_lines = 0

    def should_count_line(self, line):
        x = re.search('^using', line) or re.search('^namespace', line) or re.search('^\s*\/\/', line) or re.search('^\s*[\(\){};]*\s*$', line) or re.search('^\s*#region', line) or re.search('^\s*#endregion', line)
        if x == None:
            return True
        return False

    def should_count_first_line(self, line):
        x = re.search('using', line) or re.search('namespace', line) or re.search('\/\/', line) or re.search('^\s*$', line) or re.search('#region', line) or re.search('#endregion', line)
        if x == None:
            return True
        return False

    def parse_source(self, source_path):
        source_lines = list()
        with open(source_path) as fp:
            line = fp.readline()
            if self.should_count_first_line(line): source_lines.append(line.rstrip())
            while line:
                line = fp.readline()
                if self.should_count_line(line): source_lines.append(line.rstrip())
            return source_lines

    def parse_project(self, project_path):
        source_files = list()
        with open(project_path) as fp:
            line = fp.readline()
            while line:
                x = re.search('Compile Include="([^"]+.cs)"', line)
                if x != None: source_files.append(PureWindowsPath(x.group(1))) 
                line = fp.readline()
            source_files.sort()
            return source_files

    def parse_sln(self, sln_path):
        project_files = list()
        with open(sln_path) as fp:
            line = fp.readline()
            while line:
                x = re.search('([^"]+.csproj)', line)
                if x != None: project_files.append(PureWindowsPath(x.group()))
                line = fp.readline()
        return project_files

    def count_lines_in_source(self, source_path):
        if source_path.suffix != '.cs':
            self.unable_to_parse.append(source_path)
        else:
            lines = list()
            try:
                lines = self.parse_source(source_path)
                #print(*lines, sep='\n')
                return len(lines)
            except Exception as inst:
                self.unable_to_parse.append(source_path)
                print("Exception: ", inst)
        return 0
            

    def count_lines_in_project(self, project_path):
        print(project_path)
        source_files = self.parse_project(project_path)
        self.number_of_files += len(source_files)
        for s in source_files:
            source_path = project_path.parents[0] / s
            self.number_of_lines += self.count_lines_in_source(source_path)
        
    def run(self, root_path, sln_file_path):
        root = PurePath("/{}".format(root_path))
        print(f"Parsing solution file {root / sln_file_path}")
        project_files = self.parse_sln(root / sln_file_path)
        for p in project_files:
            self.count_lines_in_project(root / p)

        print()
        print()
        print("Files: {} Lines: {}".format(self.number_of_files, self.number_of_lines))
        print("Unable to parse: {}".format(len(self.unable_to_parse)))
        print(*self.unable_to_parse, sep="\n")

#
# Example of calling script for a solution file located at C:\src-root\PS.Everything.sln
#
CountLinesOfCode().run("src-root", "PS.Everything.sln")