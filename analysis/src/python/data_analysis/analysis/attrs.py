from typing import List, Tuple, Union

import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style='whitegrid', font_scale=2, rc={"lines.linewidth": 5, "lines.markersize": 15})

AttrType = Union[str, Tuple[str, List[str]]]


class Attr:
    """
    Attribute is class for categorical variables which contain information about it's name,
    values and colors for each color
    """

    def __init__(self, name: str, values: List[str], colors: List[Tuple[float, float, float]]):
        self.name = name
        self.values = values
        self.palette = {value: color for value, color in zip(values, colors)}


""" Dict for default variables. """
ATTRS = {
    'difficulty':
        Attr('difficulty',
             ['easy', 'medium', 'hard'],
             [(0.98, 0.73, 0.62), (0.98, 0.41, 0.28), (0.79, 0.09, 0.11)]),
    'complexity':
        Attr('complexity',
             ['shallow', 'middle', 'deep'],
             [(0.77, 0.85, 0.93), (0.41, 0.68, 0.83), (0.12, 0.44, 0.70)]),
    'scope':
        Attr('scope',
             ['small', 'medium', 'wide'],
             [(0.93, 0.82, 0.79), (0.73, 0.47, 0.59), (0.17, 0.11, 0.24)]),
    'level':
        Attr('level',
             ['low', 'average', 'high'],
             [(0.77, 0.91, 0.75), (0.45, 0.76, 0.46), (0.13, 0.54, 0.26)]),
    'client':
        Attr('client',
             ['idea', 'web'],
             [(0.52, 0.18, 0.44), (0.44, 0.49, 0.69)]),
}


def get_attr(attr: AttrType) -> Attr:
    """ Get attribute from name or pair of name and values. """

    if isinstance(attr, str):
        if attr in ATTRS:
            return ATTRS[attr]
        else:
            return Attr(attr, [], [])

    name, values = attr
    colors = sns.color_palette(n_colors=len(values))
    return Attr(name, values, colors)


def draw_base_attrs():
    """ Draw color pallets of default attributes. """

    sns.set_theme(style='whitegrid', font_scale=2, rc={"lines.linewidth": 5, "lines.markersize": 15})

    for attr in ATTRS.values():
        print(attr.name, ' -> '.join(attr.values), sep='\n')
        sns.palplot(attr.palette.values())
        plt.show()
