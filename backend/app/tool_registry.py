TOOLS={
"mone_search_customer":{"description":"Search workshop customers","confirmation":False},
"mone_get_project":{"description":"Read a project","confirmation":False},
"mone_calculate_price":{"description":"Calculate project price","confirmation":False},
"mone_cutlist_estimate":{"description":"Estimate woodworking cut list","confirmation":False},
"mone_reverse_engineer_image":{"description":"Analyze furniture image","confirmation":False},
"mone_create_project":{"description":"Create a project","confirmation":True},
"mone_update_customer":{"description":"Update customer","confirmation":True},
"mone_approve_price":{"description":"Approve a price","confirmation":True},
"mone_create_manufacturing_order":{"description":"Create manufacturing order","confirmation":True},
"mone_export":{"description":"Export manufacturing data","confirmation":True},
}
def is_registered(name): return name in TOOLS
def public_tools(): return [{"name":n,**v} for n,v in TOOLS.items()]
