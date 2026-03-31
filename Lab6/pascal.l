%{
#include <stdio.h>
%}

/* ── Definitions ── */
letter     [a-zA-Z]
digit      [0-9]
id         {letter}({letter}|{digit})*
digits     {digit}+
opt_frac   (\.{digits})?
opt_exp    (E[+\-]?{digits})?
num        {digits}{opt_frac}{opt_exp}

%%

[ \t\n]+          ; 

"{"[^}]*"}"       { printf("COMMENT:    %s\n", yytext); }

"program"         { printf("KEYWORD:    program\n"); }
"var"             { printf("KEYWORD:    var\n"); }
"integer"         { printf("KEYWORD:    integer\n"); }
"real"            { printf("KEYWORD:    real\n"); }
"function"        { printf("KEYWORD:    function\n"); }
"procedure"       { printf("KEYWORD:    procedure\n"); }
"begin"           { printf("KEYWORD:    begin\n"); }
"end"             { printf("KEYWORD:    end\n"); }
"if"              { printf("KEYWORD:    if\n"); }
"then"            { printf("KEYWORD:    then\n"); }
"else"            { printf("KEYWORD:    else\n"); }
"while"           { printf("KEYWORD:    while\n"); }
"do"              { printf("KEYWORD:    do\n"); }
"not"             { printf("KEYWORD:    not\n"); }
"array"           { printf("KEYWORD:    array\n"); }
"of"              { printf("KEYWORD:    of\n"); }

":="              { printf("ASSIGNOP:   :=\n"); }

"<="              { printf("RELOP:      <=\n"); }
">="              { printf("RELOP:      >=\n"); }
"<>"              { printf("RELOP:      <>\n"); }
"<"               { printf("RELOP:      <\n"); }
">"               { printf("RELOP:      >\n"); }
"="               { printf("RELOP:      =\n"); }

"or"              { printf("ADDOP:      or\n"); }
"+"               { printf("ADDOP:      +\n"); }
"-"               { printf("ADDOP:      -\n"); }

"div"             { printf("MULOP:      div\n"); }
"mod"             { printf("MULOP:      mod\n"); }
"and"             { printf("MULOP:      and\n"); }
"*"               { printf("MULOP:      *\n"); }
"/"               { printf("MULOP:      /\n"); }

";"               { printf("PUNCT:      semicolon\n"); }
":"               { printf("PUNCT:      colon\n"); }
","               { printf("PUNCT:      comma\n"); }
"."               { printf("PUNCT:      dot\n"); }
"("               { printf("PUNCT:      (\n"); }
")"               { printf("PUNCT:      )\n"); }
"["               { printf("PUNCT:      [\n"); }
"]"               { printf("PUNCT:      ]\n"); }
".."              { printf("PUNCT:      ..\n"); }

{num}             { printf("NUM:        %s\n", yytext); }
{id}              { printf("ID:         %s\n", yytext); }

.                 { printf("UNKNOWN:    %s\n", yytext); }

%%

int yywrap(void) {
    return 1;
}

int main() {
    printf("Pascal Subset Lexer\n");
    printf("Enter Pascal code (Ctrl+Z to stop):\n\n");
    yylex();
    return 0;
}