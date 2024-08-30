from parsimonious import Grammar, NodeVisitor
from collections.abc import Mapping
from collections import namedtuple
import random
import math
"""
File summary
In this file, we will define the grammar of STLU inputs regardless of the strong or weak.
"""
grammar_text = (r''' 
Formula = _ flag _ "," _ sub_formula _    
sub_formula = ( _ globally _ ) / ( _ eventually _ ) / ( _ until _ ) / ( _ expr _ ) / ( _ paren_formula _ )
paren_formula = "(" _ sub_formula _ ")"
globally = "G" interval sub_formula 
eventually = "E" interval sub_formula 
until = "U" interval "(" sub_formula "," sub_formula ")" 
interval = _ "[" _ bound  _ "," _ bound _ "]" _
expr = or / and / implies / npred / pred 
or = "(" _ sub_formula _ "|" _ sub_formula _ ")" 
and = "(" _ sub_formula _ "&" _ sub_formula _ ")" 
implies = "(" _ sub_formula _ "->" _ sub_formula _ ")"
npred = "!" _ sub_formula 
pred = constraint / atom 
constraint =  term _ relop _ term
term = infix / var
infix = "{" _ term _ arithop _ term _ "}"
var = _ id _
atom = _ id _
bound = param / num 
param =  id "?" _ num ";" num _ 
id = ~r"[a-zA-z\d]+"
num = ~r"[\+\-]?\d*(\.\d+)?"
relop = ">=" / "<=" / "<" / ">" / "=="
arithop = "+" / "-" / "*" / "/"
flag = "w" / "s"
_ = ~r"\s"*
''')

_grammar = Grammar(grammar_text)

""" AVL tree traversal"""
class TLVisitor(NodeVisitor):
    def visit_Formula(self, node, children):
        _, flag, _, _, _, subformula, _ = children
        return Formula(flag, subformula)

    def visit_sub_formula(self, node, children):
        return children[0][1]

    def visit_paren_formula(self, node, children):
        return children[2]

    def visit_globally(self, node, children):
        _, interval, formula = children
        return Globally(interval, formula)
        
    def visit_eventually(self, node, children):
        _, interval, formula = children
        return Eventually(interval, formula)
        
    def visit_until(self, node, children):
        _, interval, _, formula1, _, formula2, _ = children
        return Until(interval, formula1, formula2)

    def visit_interval(self, node, children):
        _, _, _, left, _, _, _, right, _, _, _  = children
        return Interval(left, right)

    def visit_expr(self, node, children):
        return children[0]

    def visit_or(self, node, children):
        _, _, left, _, _, _, right, _, _ = children
        return Or(left, right)

    def visit_and(self, node, children):
        _, _, left, _, _, _, right, _, _ = children
        return And(left, right)
    #implies = "(" _ formula _ "->" _ formula _ ")"
    def visit_implies(self, node, children):
        _, _, left, _, _, _, right, _, _ = children
        return Implies(left, right)

    def visit_npred(self, node, children):
        _, _, right = children
        return Not(right)

    def visit_pred(self, node, children):
        return children[0]

    def visit_constraint(self, node, children):
        left, _, relop, _, right = children
        return Constraint(relop, left, right)
    
    def visit_term(self, node, children):
        return children[0]

    def visit_infix(self, node, children):
        _, _, left, _, arithop, _, right, _, _ = children
        return Expr(arithop, left, right)

    def visit_atom(self, node, children):
        return Atom(children[1])

    def visit_var(self, node, children):
        return Var(children[1])
    
    def visit_bound(self, node, children):
        return children[0]

    def visit_param(self, node, children):
        name, _, _, left, _, right, _ = children
        return Param(name, left, right)

    def visit_id(self, node, children):
        return node.text

    def visit_num(self, node, children):
        return Constant(node.text)

    def visit_relop(self, node, children):
        return node.text

    def visit_arithop(self, node, children):
        return node.text
      
    def visit_flag(self, node, children):
        return node.text
      
    def generic_visit(self, node, children):
        if children:
            return children

class Formula(namedtuple('Formula',['flag', 'subformula'])):
    def children(self):
        return [self.subformula]
    def __repr__(self):
        return "{}, {}".format(self.flag, self.subformula)
class Globally(namedtuple('G',['interval','subformula'])):
    def children(self):
        return [self.subformula]
    def __repr__(self):
        return "G{}({})".format(self.interval, self.subformula)

class Eventually(namedtuple("E", ['interval','subformula'])):
    def children(self):
        return [self.subformula]
    def __repr__(self):
        return "E{}({})".format(self.interval, self.subformula)
class Until(namedtuple('U',['interval','left', 'right'])):
    def children(self):
        return [self.left, self.right]
    def __repr__(self):
        return "U{}{}{}".format(self.interval, self.left, self.right)

class Interval(namedtuple("Interval", ['left','right'])):
    def __repr__(self):
        return "[{},{}]".format(self.left, self.right)
    def children(self):
        return [self.left, self.right]

class Or(namedtuple("Or",["left", "right"])):
    def __repr__(self):
        return "({} | {})".format(self.left, self.right)
    def children(self):
        return [self.left,self.right]

class And(namedtuple("And",["left", "right"])):
    def __repr__(self):
        return "({} & {})".format(self.left, self.right)
    def children(self):
        return [self.left,self.right]

class Implies(namedtuple("Implies",["left", "right"])):
    def __repr__(self):
        return "({} => {})".format(self.left, self.right)
    def children(self):
        return [self.left,self.right]
      
class Not(namedtuple("Negation", ['subformula'])):
    def __repr__(self):
        return "(! {})".format(self.subformula)
    def children(self):
        return [self.subformula]

class Constraint(namedtuple("Constraint",["relop", "term", "bound"])):
    def __repr__(self):
        return "({} {} {})".format(self.term, self.relop, self.bound)
    def children(self):
        return [self.term, self.bound]
    
class Expr(namedtuple("Var", ["arithop", "left", "right"])):
    def __repr__(self):
        return "{{{}{}{}}}".format(self.left, self.arithop, self.right)
    
class Atom(namedtuple("Atom", ["name"])):
    def __repr__(self):
        return "{}".format(self.name)

class Var(namedtuple("Var", ["name"])):
    def __repr__(self):
        return "{}".format(self.name)

class Param(namedtuple("Param", ["name", "left", "right"])):
    def __repr__(self):
        return "{}? {};{} ".format(self.name, self.left, self.right)

class Constant(float):
    pass

def parse(tlStr):
    return TLVisitor().visit(_grammar["Formula"].parse(tlStr))
    #return _grammar["formula"].parse(tlStr)
    
    
def interval_generator():
    interval_num1 = random.randint(0,20)
    interval_num2 = random.randint(interval_num1 + 1, interval_num1 + 50)
    interval = " [ " + str(interval_num1) + " , " + str(interval_num2)+ " ] "
    return interval
  

def stl_generator1(flag_num):
    if flag_num not in [0,1]:
        print("flag need to chosen from 0 and 1 where 0 is strong and 1 is weak")
    rule1_lst = ["E", "G", "U"]
    rule2_lst = ["&", "|"]
    relop_lst = [">=" , "<=" , "<" , ">" , "=="]
    flag_lst = ["s", "w"]
    flag = flag_lst[flag_num]
    negate_lst = ["", "! "]
    rand_rule1 = random.randint(0,2)
    rand_rule2 = random.randint(0,1)
    rand_relop = random.randint(0,4)
    rule1 = rule1_lst[rand_rule1]
    rule2 = rule2_lst[rand_rule2]
    relop = relop_lst[rand_relop]
    negate = negate_lst[random.randint(0,1)]
    interval = interval_generator()

    if rand_rule1 == 2:
      formula1 = "( A " + rule2 +" " + negate + "c " + str(relop_lst[random.randint(0,4)]) + " "+ str(random.randint(0,1000))+ " )"
      formula2 = "b "+ relop + " " + str(random.randint(0,1000))
      output_str = flag + " , " + rule1 + interval + "("+ formula1 + "," + formula2 + ")"
      return output_str
    else:
      formula1 = "( A " + rule2 +" " + negate + "c " + str(relop_lst[random.randint(0,4)]) + " "+ str(random.randint(0,1000))+ " )"
      output_str = flag +  " , " + rule1 + interval + formula1
      return output_str
      
res = stl_generator1(1)
print(res)      
print(parse(res))
# Until's interval need to be configured 
#result = parse('a<b')
# result2 = parse("µ 0.95 1 -1 w")


#print(result)
# print(result2)