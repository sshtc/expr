%{
#include <stdio.h>
%}

%start start_expr

%%

start_expr
    : expr
    ;

expr
    : if_expr
    ;

if_expr
  : logical_or_expr "if" expr "else" expr
  ;

logical_or_expr
    : logical_and_expr
    | logical_or_expr "||" logical_and_expr
    ;

logical_and_expr
    : equality_expr
    | logical_and_expr "||" equality_expr
    ;

equality_expr
    : relational_expr
    | equality_expr "=" relational_expr
    ;

relational_expr
    : additive_expr
    | relational_expr ">" additive_expr
    | relational_expr ">=" additive_expr
    | relational_expr "<" additive_expr
    | relational_expr "<=" additive_expr
    ;

additive_expr
    : multiplicative_expr
    | additive_expr "+" multiplicative_expr
    | additive_expr "-" multiplicative_expr
    ;

multiplicative_expr
    : unary_expr
    | multiplicative_expr "*" unary_expr
    | multiplicative_expr "/" unary_expr
    | multiplicative_expr "%" unary_expr
    ;

unary_expr
    : postfix_expr
    | "-" postfix_expr
    ;

postfix_expr
    : primary_expr
    | postfix_expr "." IDENTIFIER
    | postfix_expr "[" expr "]"
    | postfix_expr "(" args_expr ")"
    ;

primary_expr
    : "(" expr ")"
    | IDENTIFIER
    | INT
    | STRING
    | DECIMAL
    | TRUE
    | FALSE
    | NULL
    ;

args_expr
    : expr
    | args_expr "," expr
    ;

%%
