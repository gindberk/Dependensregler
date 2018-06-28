#detta är ett slaskdokument där jag skriver över sådant som jag inte vill ha i filerna men ändå vill ha kvar.

#följande regler är från "temp_script_r.txt
{
    hp postag "HP" and <--. (v postag "VB") and $- (k form "," and $- (n postag "NN")) and not $-- (i deprel "IR" and $++ i2 deprel "JR")
    ::
    delete node k;# copy node d after node n;#split before node hp and after group v;# after node n;
}

#används på sjuksköterskeexemplet##############################################
{
    hp postag "HP" and <--. (v postag "VB") and $- (n postag "NN" and .<-- (d postag "DT")) and not $-- (i deprel "IR" and $++ i2 deprel "JR")
    ::
    copy node n after node n; copy node d after node n;# copy node d after node n;#split before node hp and after group v;# after node n;
}

#används på medicinexemplet - tar bort den relativa satsen#####################
{
    hp postag "HP" and .-> (n postag "NN") and $- (n postag "NN" and $- (d postag "DT"))
    ::
    delete group hp;
}
###############################################################################

{
    hp postag "HP" and $- (n postag "NN" and $- (d postag "DT" and $- (n2 postag "NN"))) and <--. (v postag "VB")
    ::
    split before node d and after group v;
}

{
    hp postag "HP" and <--. (v postag "VB") and $- (n postag "NN") and not $-- (i deprel "IR" and $++ i2 deprel "JR")
    ::
    copy node n after node n;# copy node d after node n;#split before node hp and after group v;# after node n;
}

{
    hp postag "HP" and $- (n postag "NN" and $- (n2 postag "NN")) and <--. (v postag "VB")
    ::
    split before node n and after group v;
}

{
    n is_top and $+ (p postag "MAD" ) and not $- (x)
    ::
    delete group n;
}

{
    n is_top and $- (d postag "DT" and not $- (x)) and not $+ (y)
    ::
    delete group n;
}
"""""Detta är konditionsträningsregeln som kan klistras in i svo, men då fuckar den upp resten av reglerna{   ab postag "AB" and <-. (v postag "VB" and ->. (n deprel "SS" ) and  -->.(x) and .<-(y) and ->.(z)) and not $-(x) and $++(p form ".")
    ::
    move node n before node v; move node ab before node p;
}"
