import os
from math import log2
from random import random
import pandas as pd
import graphviz

def save_graph_as_jpg(graph, filename):
    graph.save('temp.dot')
    src = graphviz.Source.from_file('temp.dot')
    src.render(filename, format="jpg")
    os.remove('temp.dot')
    os.remove(filename)


def safe_log2(value):
    if value > 0:
        return log2(value)
    else:
        return 0


def calculate_entropy(yes_count, no_count, total_rows):
    return -(yes_count/total_rows) * safe_log2(yes_count/total_rows) - \
        (no_count/total_rows) * safe_log2(no_count/total_rows)


def calculate_category_gain(df, category_name):
    print(category_name)
    result = df.columns[-1]
    total_rows = df[result].count()
    yes_count = sum((df[result] == "y") | (df[result] == "Y"))
    no_count = sum((df[result] == "n") | (df[result] == "N"))
    entropy = calculate_entropy(yes_count, no_count, total_rows)

    values = df[category_name].unique()

    gain = entropy

    for value in values:
        vdf = df[df[category_name] == value]
        value_total = vdf[vdf.columns[0]].count()
        value_yes = sum((vdf[result] == "y") | (vdf[result] == "Y"))
        value_no = sum((vdf[result] == "n") | (vdf[result] == "N"))
        value_entropy = calculate_entropy(value_yes, value_no, value_total)
        value_gain = (value_total / total_rows) * value_entropy
        # print("{} Entropy: {}, Gain: {}".format(value, value_entropy, value_gain))
        gain -= value_gain

    # print("{} Gain: {}", category_name, gain)

    return gain


def lerp(a, b, alpha):
    c = [0, 0, 0]
    for i in range(0, len(a)-1):
        c[i] = int(alpha*b[i] + (1.0-alpha)*a[i])
    return tuple(c)


def rgb_to_hex(rgb):
    return '%02x%02x%02x' % rgb

# def rgb_to_hex(rgb):
#     return ('{:X}{:X}{:X}').format(int(rgb[0]), rgb[1], rgb[2])


def add_frame_to_graph_id3(dataframe, graph, parent_name="", edge_name=""):
    node_name = ""
    color = "white"
    node_id = str(random())

    result = dataframe.columns[-1]
    total_rows = dataframe[result].count()
    yes_count = sum((dataframe[result] == "y") | (dataframe[result] == "Y"))
    no_count = sum((dataframe[result] == "n") | (dataframe[result] == "N"))

    break_on_category = ""

  #  print(f"""Processing data frame:
  #   {dataframe}
  # 
  #   Total rows: {total_rows}
  #   Yes count: {yes_count}
  #   No count: {no_count}
  #  
  #   """)

# Tweek the entropy percentage and/or number of rows
    if yes_count/total_rows > .8:
        node_name = f"Yes {int((yes_count/total_rows)*100)}%"
        node_id += node_name
        color = "green"
    elif no_count/total_rows > .8: #emperical
        node_name = f"No {int((no_count/total_rows)*100)}%"
        node_id += node_name
        color = "red"
    elif len(dataframe.columns[0:-1]) > 0 and total_rows > 1:
        largest_gain = -1
        for category in dataframe.columns[0:-1]:
            gain = calculate_category_gain(dataframe, category)
            if gain > largest_gain:
                largest_gain = gain
                node_name = category
                break_on_category = category

        # Break on category
        node_id += node_name
    else:
        node_name = "Yes: {}%, No: {}%".format(int(100*(yes_count/total_rows)), int(100*(no_count/total_rows)))
        node_id += "Yes-{}-percent-No-{}-percent".format(int(100*(yes_count/total_rows)), int(100*(no_count/total_rows)))
        alpha = yes_count/total_rows
        color = f"#{rgb_to_hex(lerp((255, 0, 0), (0, 255, 0), alpha))}"

    entries = dataframe[dataframe.columns[0]].count()
    graph.node(node_id, f'''<
        <TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" BGCOLOR="{color}">
          <TR>
            <TD>{node_name}</TD>
          </TR>
          <TR>
            <TD>{entries} rows</TD>
          </TR>
        </TABLE>>''')

    if edge_name:
        graph.edge(parent_name, node_id, label=str(edge_name))

    if break_on_category:
        # print(f"Breaking on category: {break_on_category}")
        values = df[break_on_category].unique()
        for value in values:
            vdf = dataframe[dataframe[break_on_category] == value]
            rows = vdf[vdf.columns[-1]].count()
            if rows > 0:
                # print(f"Value: {value}")
                # print(vdf)
                vdf = vdf.drop(columns=[break_on_category])
                # print(f"Dropping column: ")
                # print(vdf)
                add_frame_to_graph_id3(vdf, graph, node_id, value)



s = graphviz.Digraph('structs', filename='structs.gv',
                     node_attr={'shape': 'plaintext'})
df = pd.read_csv('outdoors-corrected.csv')
print(df)
add_frame_to_graph_id3(df, s)
save_graph_as_jpg(s, "outdoors")


