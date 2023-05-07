#!/usr/bin/python3
import csv


text = ""
new_headers = ['short name', 'link', 'cost per part', 'total # req', 'total cost']
all_assemblies_cost = 0

# helper functions
def table_header(assembly):
    txt = "\n\n"
    txt += f"## Parts for {assembly} assembly\n\n"
    txt += f"| {' | '.join(new_headers)} |\n"
    txt += "|---" * len(new_headers) + "|\n"
    return txt

def assembly_cost(total_sub_assembly_cost, nb_subassy_req):
    if nb_subassy_req == 1:
        return f"\nCost to build this assembly: ${round(total_sub_assembly_cost, 2)}"
    else:
        return f"\nCost to build these assemblies: ${round(total_sub_assembly_cost / nb_subassy_req, 2)} "\
               f"* {int(nb_subassy_req)} assemblies = ${round(total_sub_assembly_cost, 2)}\n"

# parse mechanical parts list
with open('parts_list.csv') as csvfile:
    reader = csv.reader(csvfile)
    headers = next(reader)
    prev_assembly = None
    total_sub_assembly_cost = 0
    nb_subassy_req = None
    for row in reader:
        assembly = row[0]
        if assembly != prev_assembly:
            if prev_assembly:  # summarize cost of subassembly
                text += assembly_cost(total_sub_assembly_cost, nb_subassy_req)
                all_assemblies_cost += total_sub_assembly_cost
                total_sub_assembly_cost = 0
            text += table_header(assembly)
            prev_assembly = assembly
        short_name = row[1]
        link = f"[{row[3]}]({row[4]})"
        costpp = float(row[5].replace('$', ''))
        nb_subassy_req = float(row[7])
        total_req = float(row[6]) * nb_subassy_req
        total_cost = costpp * total_req
        total_sub_assembly_cost += total_cost
        text += f"| {' | '.join([short_name, link, f'${costpp}', str(int(total_req)), f'${total_cost}'])} |\n"
    text += assembly_cost(total_sub_assembly_cost, nb_subassy_req)
    all_assemblies_cost += total_sub_assembly_cost

# parse digikey parts list
text += table_header('electrical')
total_ext_price = 0
with open('digikey_bom.csv') as csvfile:
    reader = csv.reader(csvfile)
    headers = next(reader)
    for row in reader:
        quantity = int(row[1])
        part_nb = row[2]
        manuf_part_nb = row[3]
        descr = row[4]
        link = f"[{part_nb}](https://www.digikey.com/en/products/result?keywords={part_nb})"
        customer_ref = row[5]
        unit_price = float(row[8])
        extended_price = float(row[9])  # digikey has volume discounts
        text += f"| {' | '.join([f'{customer_ref}: {descr}', link, f'${unit_price}', str(quantity), f'${extended_price}'])} |\n"
        total_ext_price += extended_price
text += assembly_cost(total_ext_price, 1)
all_assemblies_cost += total_ext_price

md_text = \
f"""
# Parts list

This file was autogenerated from the [mechanical parts list](parts_list.csv) and [digikey BOM](digikey_bom.csv)
and should consist of the same parts, just presented in a more readable format. The Digikey csv file can be uploaded
to Digikey.com directly to create a shopping cart.
Before you place an order, please double check that you have all parts in the right quantities.

The total cost comes out to be **${round(all_assemblies_cost, 2)}** without discounts. If you are an educational builder,
please join the Slack workspace and enquire about any discounts.

{text}
"""

with open('README.md', 'w') as ofile:
    ofile.writelines(md_text)
