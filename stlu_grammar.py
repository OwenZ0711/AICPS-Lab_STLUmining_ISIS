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
formula = ( _ globally _ ) / ( _ eventually _ ) / ( _ until _ ) / ( _ expr _ ) / ( _ paren_formula _ ) / ( _ mu _ )
paren_formula = "(" _ formula _ ")"
globally = "G" interval formula flag
eventually = "E" interval formula flag
until = "U" interval "(" formula "," formula ")" flag
mu = "µ" "(" num _ num _ num ")" flag
interval = _ "[" _ bound  _ "," _ bound _ "]" _
expr = or / and / implies / npred / pred 
or = "(" _ formula _ "|" _ formula _ ")" flag
and = "(" _ formula _ "&" _ formula _ ")" flag
implies = "(" _ formula _ "->" _ formula _ ")"
npred = "!" _ formula flag
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
flag = "w" / "s" / ""
_ = ~r"\s"*
''')

_grammar = Grammar(grammar_text)

""" AVL tree traversal"""
class TLVisitor(NodeVisitor):

    def visit_formula(self, node, children):
        return children[0][1]

    def visit_paren_formula(self, node, children):
        return children[2]

    def visit_globally(self, node, children):
        _, interval, formula, flag = children
        return Globally(interval, formula, flag)
        
    def visit_eventually(self, node, children):
        _, interval, formula, flag = children
        return Eventually(interval, formula, flag)
    
    def visit_mu(self, node, children):
        _,_, th, _, cl, _, t, _, flag = children
        return Mu(th,cl,t, flag)
        
    def visit_until(self, node, children):
        _, interval, _, formula1, _, formula2, _, flag = children
        return Until(interval, formula1, formula2, flag)

    def visit_interval(self, node, children):
        _, _, _, left, _, _, _, right, _, _, _  = children
        return Interval(left, right)

    def visit_expr(self, node, children):
        return children[0]

    def visit_or(self, node, children):
        _, _, left, _, _, _, right, _, _, flag = children
        return Or(left, right, flag)

    def visit_and(self, node, children):
        _, _, left, _, _, _, right, _, _, flag = children
        return And(left, right, flag)
    #implies = "(" _ formula _ "->" _ formula _ ")"
    def visit_implies(self, node, children):
        _, _, left, _, _, _, right, _, _, flag = children
        return Implies(left, right, flag)

    def visit_npred(self, node, children):
        _, _, right, flag = children
        return Not(right, flag)

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

class Globally(namedtuple('G',['interval','subformula', 'flag'])):
    def children(self):
        return [self.subformula]
    def __repr__(self):
        return "G{}({})flag: {}".format(self.interval, self.subformula, self.flag)

class Eventually(namedtuple("E", ['interval','subformula', 'flag'])):
    def children(self):
        return [self.subformula]
    def __repr__(self):
        return "{}F{}{}".format(self.flag, self.interval, self.subformula)
    
class Until(namedtuple('U',['interval','left', 'right' , 'flag'])):
    def children(self):
        return [self.left, self.right]
    def __repr__(self):
        return "U{}{}{}flag: {}".format(self.interval, self.left, self.right, self.flag)

class Interval(namedtuple("Interval", ['left','right'])):
    def __repr__(self):
        return "[{},{}]".format(self.left, self.right)
    def children(self):
        return [self.left, self.right]

class Or(namedtuple("Or",["left", "right", "flag"])):
    def __repr__(self):
        return "({} | {}, flag:{})".format(self.left, self.right, self.flag)
    def children(self):
        return [self.left,self.right]

class And(namedtuple("And",["left", "right", 'flag'])):
    def __repr__(self):
        return "({} {}& {})".format(self.left, self.flag, self.right)
    def children(self):
        return [self.left,self.right]

class Implies(namedtuple("Implies",["left", "right"])):
    def __repr__(self):
        return "({} => {}), flag:{}".format(self.left, self.right, self.flag)
    def children(self):
        return [self.left,self.right, self.flag]
      
class Mu(namedtuple('µ', ['th', 'cl', 't', "flag"])):
    def __repr__(self):
        return "(μ conf:{} sigma:[+-{}] mean:{}, flag: {})".format(self.t, self.cl, self.th, self.flag)
    def children(self):
        return[self.th, self.cl, self.t, self.flag]
      
class Not(namedtuple("Negation", ['subformula', "flag"])):
    def __repr__(self):
        return "(! {}, flag: {})".format(self.subformula, self.flag)
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
    return TLVisitor().visit(_grammar["formula"].parse(tlStr))
    #return _grammar["formula"].parse(tlStr)
    
    
def interval_generator():
    interval_num1 = random.randint(0,20)
    interval_num2 = random.randint(interval_num1 + 1, interval_num1 + 50)
    interval = " [ " + str(interval_num1) + " , " + str(interval_num2)+ " ] "
    return interval
  

def stl_generator1(flag_num):
    if flag_num not in [0,1]:
        print("flag need to chosen from 0 and 1 where 0 is strong and 1 is weak")
    rule1_lst = ["E", "G", "U", "µ"]
    rule2_lst = ["&", "|"]
    relop_lst = [">=" , "<=" , "<" , ">" , "=="]
    flag_lst = ["s", "w"]
    flag = flag_lst[flag_num]
    negate_lst = ["", "! "]
    rand_rule1 = random.randint(0,3)
    rand_rule2 = random.randint(0,1)
    rand_relop = random.randint(0,4)
    rule1 = rule1_lst[rand_rule1]
    rule2 = rule2_lst[rand_rule2]
    relop = relop_lst[rand_relop]
    negate = negate_lst[random.randint(0,1)]
    interval = interval_generator()
    if rand_rule1 == 3:
      mean = str(random.randint(0,100))
      sigma = str(random.randint(0,10))
      conf = str(random.uniform(0,1))
      output_str = rule1 + "(" + mean + " " + sigma + " " + conf + ")" + flag
      return output_str

    if rand_rule1 == 2:
      formula1 = "( A " + rule2 +" " + negate + "c " + str(relop_lst[random.randint(0,4)]) + " "+ str(random.randint(0,1000))+ " )" + flag
      formula2 = "b "+ relop + " " + str(random.randint(0,1000))
      output_str = rule1 + interval + "("+ formula1 + "," + formula2 + ")" + flag
      return output_str
    else:
      formula1 = "( A " + rule2 +" " + negate + "c " + str(relop_lst[random.randint(0,4)]) + " "+ str(random.randint(0,1000))+ " )" + flag
      output_str = rule1 + interval + formula1 + flag
      return output_str
      
res = stl_generator1(1)
print(res)      
print(parse(res))
# Until's interval need to be configured 
#result = parse('a<b')
# result2 = parse("µ 0.95 1 -1 w")

#print(result)
# print(result2)