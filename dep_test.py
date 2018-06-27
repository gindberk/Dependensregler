import copy
import apply_rules
import SAPIS
import os

class Auto_Rules:
    """docstring for ."""
    def __init__(self, gold, original, new):
        #super().__init__()
        self.gold = gold
        self.original = original
        self.new = new

    def convert_conll(self, taggedText):
        "konvertera till strangar och listor"
        conll_list = []
        temp_str = ""
        for token in taggedText:
            if token != '\n':
                temp_str += token
            else:
                conll_list.append(temp_str)
                temp_str = ""

        return conll_list

    def flatten_tree(self, deep_list):
        "Konvertera lista med trad till en stor strang"
        flattened_list = []
        for element in deep_list:
            for value in element:
                flattened_list.append(value)

        return flattened_list

    def compare_aprox(self, flat_result, flat_gold):
        "Jamfor i stora drag"
        aprox_equals = True
        if flat_gold != flat_result:
            aprox_equals == False

        return aprox_equals
    def compare_prec(self, list1, list2):
        "Jamfor rad for rad"
        errors = []
        for one, two in zip(list1, list2):
            for o,t in zip(one, two):
                if r != g:
                    errors.append((r,g))

        return errors


    def user_input(self, error_list, new_simple, gold, original, new_original):
        "godkanna forenkling pa ny text, om godkand lagga in i guldstandard"
        if not error_list:
            print("Alla trad ar enligt guldstandard")

        else:
            print("Dessa trad blir felaktiga")
            for line in error_list:
                print(line)

        print(new_simple)
        print(new_original)
        approve = raw_input('Godkanna nytt trad? (y/n): ')


        if approve == "y" and not error_list:
            with open ("ConLL/gold.conllx", "a") as goldfile:
        	       goldfile.write(new_simple)
            with open ("ConLL/original.conllx", "a") as orgfile:
                orgfile.write(new_original)
                orgfile.write('\n')
            self.save_rules()


    def save_rules(self):
        "Uppdaterar regler nar arbetsversioner blivit godkanda"
        rules = ["script/script_p2a.txt", "script/script_prox.txt",
                 "script/script_svo.txt", "script/script_split_a.txt",
                 "script/script_split_k.txt", "script/script_split_r.txt",
                 "script/script_qi.txt"]

        temp_rules = ["temp_scripts/temp_script_p2a.txt",
                      "temp_scripts/temp_script_prox.txt",
                      "temp_scripts/temp_script_svo.txt",
                      "temp_scripts/temp_script_split_a.txt",
                      "temp_scripts/temp_script_split_k.txt",
                      "temp_scripts/temp_script_split_r.txt",
                      "temp_scripts/temp_script_qi.txt"]

        for rule, temp in zip(rules, temp_rules):
            with open(temp, 'r') as temprule:
                data = temprule.read()
            os.remove(rule)
            with open (rule, "w") as newrule:

        	       newrule.write(data)


    def load_new_original(self):
        original_tree = ""
        with open("ConLL/newtree.conllx") as n:
            for line in n:
                original_tree += line

            return original_tree

    def main(self):
        "kor funktioner"
        if (os.stat("ConLL/gold.conllx").st_size > 0 and
        os.stat("ConLL/original.conllx").st_size > 0):
            result = apply_rules.get_result(self.original)

            result_list = self.convert_conll(result)
            gold_list = self.convert_conll(result)
            original_list = self.convert_conll(self.original)

            flat_result = copy.copy(result_list)
            flat_gold = copy.copy(gold_list)

            flat_result = self.flatten_tree(flat_result)
            flat_gold = self.flatten_tree(flat_gold)

            equals = self.compare_aprox(flat_result, flat_gold)

        else:
            equals = True

        #new_tree = get_conll(USER INPUT)
        #new_tree = convert_conll(new_tree)
        new_tree = apply_rules.get_result(self.new)
        self.new = self.load_new_original()


        if equals == True:
            errors = []
            self.user_input(errors, new_tree, self.gold, self.original,
                            self.new)
        else:
            errors = compare_prec(gold_list, result_list)
            self.user_input(errors, new_tree, self.gold, self.original,
                            self.new)



if __name__ == '__main__':
    regler = Auto_Rules("ConLL/gold.conllx","ConLL/original.conllx",
                        "ConLL/newtree.conllx")
    regler.main()
