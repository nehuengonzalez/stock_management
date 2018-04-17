import pulp


# ---model indices denominations--------------------------------------------------------
COIL_DEN = "b"
"""
Coil index denomination. Each possible coil on catalog has an unique index COIL_DEN
"""
PROD_DEN = "p"
"""
Product index denomination. Each product has an unique index PRDO_DEN
"""

# ---Variable names and indices positions-----------------------------------------------
TOTAL_COILS_NAME = "Total_Coils_z"
TOTAL_WASTE_NAME = "Total_Waste_d"
PRODUCT_ASSIGNMENT_NAME = "Assignment_Variables_x(%s,%s)" % (COIL_DEN, PROD_DEN)
COIL_USAGE_NAME = "Coil_Usage_Variable_x(%s)" % (COIL_DEN)

PRODUCT_ASSIGNMENT_IDS = [COIL_DEN, PROD_DEN]
COIL_USAGE_IDS = [COIL_DEN]


# ---minimum number of coils model (1)--------------------------------------------------
def min_coils_lp(coil_widths, product_widths, wastes ,waste_max, instance_name=""):
    """
    This method creates an instance of minimum number of coils model.

    :param coil_widths: A list with the widths of the available coils in catalog
    :param product_widths: A list with the widths of the products.
    :param waste_max: Maximum acceptable waste.
    :return: A pulp.LpProblem instance
    """

    prob = pulp.LpProblem("MCP instance: %s" % instance_name, pulp.LpMinimize)

    # ---Total coil usage---------------------------------------------------------------
    z_total = pulp.LpVariable(TOTAL_COILS_NAME, lowBound=0, cat=pulp.LpInteger)

    # ---Coil usage variables-----------------------------------------------------------
    xb_combs = list(range(len(coil_widths)))

    xb = pulp.LpVariable.dicts(COIL_USAGE_NAME, xb_combs, lowBound=0
                                                        , upBound=1
                                                        , cat=pulp.LpInteger)

    # ---Product assignment variables---------------------------------------------------
    xbp_combs = []
    for b in range(len(coil_widths)):
        for p in range(len(product_widths)):
            xbp_combs.append((b, p))

    xbp = pulp.LpVariable.dicts(PRODUCT_ASSIGNMENT_NAME, xbp_combs, lowBound=0
                                                                  , upBound=1
                                                                  , cat=pulp.LpInteger)

    # ---Objective function Eq.(1)------------------------------------------------------
    prob += z_total

    # ---Total amount of coils constraint Eq.(2)----------------------------------------
    prob += z_total + sum(-1 * xb[b_id] for b_id in range(len(coil_widths))) == 0

    # ---Maximum waste constraint-------------------------------------------------------
    restr = ""
    for b_id in range(len(coil_widths)):
        for p_id in range(len(product_widths)):
            restr += " + %f * xbp[(%d,%d)]" % (wastes[b_id][p_id], b_id, p_id)
    restr += " <= %f " % waste_max
    prob += eval(restr)

    # ---Product assignment constraint--------------------------------------------------
    for p_id in range(len(product_widths)):
        prob += sum([xbp[(b_id, p_id)] for b_id in range(len(coil_widths))]) == 1

    # ---Coil usage constraint----------------------------------------------------------
    for (b_id, p_id) in [(b, p) for p in range(len(product_widths))
                                for b in range(len(coil_widths))]:
        prob += xb[b_id] >= xbp[(b_id, p_id)]

    return prob


# ---minimum waste model (1)--------------------------------------------------
def min_coils_lp(coil_widths, product_widths, wastes, coils_max, instance_name=""):
    """
    This method creates an instance of minimum number of coils model.

    :param coil_widths: A list with the widths of the available coils in catalog
    :param product_widths: A list with the widths of the products.
    :param coils_max: Maximum acceptable coils.
    :return: A pulp.LpProblem instance
    """

    prob = pulp.LpProblem("MWP instance: %s" % instance_name, pulp.LpMinimize)

    # ---Total waste -------------------------------------------------------------------
    d_total = pulp.LpVariable(TOTAL_WASTE_NAME, lowBound=0, cat=pulp.LpContinuous)

    # ---Total coil usage---------------------------------------------------------------
    z_total = pulp.LpVariable(TOTAL_COILS_NAME, lowBound=0, cat=pulp.LpInteger)

    # ---Coil usage variables-----------------------------------------------------------
    xb_combs = list(range(len(coil_widths)))

    xb = pulp.LpVariable.dicts(COIL_USAGE_NAME, xb_combs, lowBound=0
                               , upBound=1
                               , cat=pulp.LpInteger)

    # ---Product assignment variables---------------------------------------------------
    xbp_combs = []
    for b in range(len(coil_widths)):
        for p in range(len(product_widths)):
            xbp_combs.append((b, p))

    xbp = pulp.LpVariable.dicts(PRODUCT_ASSIGNMENT_NAME, xbp_combs, lowBound=0
                                , upBound=1
                                , cat=pulp.LpInteger)

    # ---Objective function Eq.(1)------------------------------------------------------
    prob += d_total

    # ---Total waste constraint---------------------------------------------------------
    restr = ""
    for b_id in range(len(coil_widths)):
        for p_id in range(len(product_widths)):
            restr += " + %f * xbp[(%d,%d)]" % (wastes[b_id][p_id], b_id, p_id)
    restr += " == d_total "
    prob += eval(restr)

    # ---Total amount of coils constraint Eq.(2)----------------------------------------
    prob += z_total == sum(xb[b_id] for b_id in range(len(coil_widths)))

    # ---Maximum number of coils constraint---------------------------------------------
    prob += z_total <= coils_max

    # ---Product assignment constraint--------------------------------------------------
    for p_id in range(len(product_widths)):
        prob += sum([xbp[(b_id, p_id)] for b_id in range(len(coil_widths))]) == 1

    # ---Coil usage constraint----------------------------------------------------------
    for (b_id, p_id) in [(b, p) for p in range(len(product_widths))
                         for b in range(len(coil_widths))]:
        prob += xb[b_id] >= xbp[(b_id, p_id)]

    return prob
