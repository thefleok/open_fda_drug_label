# testing functions for open_fda_drug_label functions and objects

from dotenv import load_dotenv
import os
import requests
from open_fda_drug_label import Drug_Label_Client, Drug, Shelf, make_drugs

# Extracting locally stored API key for testing
load_dotenv()
API_KEY = os.getenv("FDA_API_KEY")

def test_DLC_init():
    client = Drug_Label_Client(API_KEY)
    # Check that a valid API key (passed from .env) actually works for this function
    assert client.api_key == API_KEY
    assert client.base_url == "https://api.fda.gov/drug/label.json"

    # Check that value error is raised for non-int API_Key with int and list and empty
    for x in [1, [3], {}, None, True]:
        try:
            client = Drug_Label_Client(x)
            assert False, f"Should have raised ValueError/TypeError for {x}"
        except TypeError:
            pass
    try:
        client = Drug_Label_Client("")
        assert False, "Should have raised ValueError for empty string"
    except ValueError:
        pass

def test_DLC_generic_search():
    client = Drug_Label_Client(API_KEY)
    # start by checking value errors:
    for x in [1, [3], {}, None, True]:
        try:
            attempt = client.generic_search("string", x)
            assert False, f"Should have raised ValueError/TypeError for {x} as non-string item"
        except (TypeError, ValueError):
            pass
        try:
            attempt = client.generic_search(x, "string")
            assert False, f"Should have raised ValueError/TypeError for {x} as non-string parameter"
        except (TypeError, ValueError):
            pass
        if not isinstance(x, bool):
            try:
                attempt = client.generic_search("a","b", x)
                assert False, f"Should have raised ValueError/TypeError for {x} as non-string"
            except (TypeError, ValueError):
                pass
                
    exact_search = client.generic_search("a","b", True)
    assert exact_search == 'openfda.a.exact:"b"'
    non_exact_search = client.generic_search("a","b")
    assert non_exact_search == 'openfda.a:"b"'


def test_DLC_search_request():
    client = Drug_Label_Client(API_KEY)
    # start by checking value errors: anything not a list:
    for x in [1, "str", {}, None, True]:
        try:
            attempt = client.search_request(x)
            assert False, f"Should have raised ValueError/TypeError for {x} as non-list"
        except (TypeError, ValueError):
            pass
        
        # check what happens when string is not passed
        if not isinstance(x, str):
            try:
                attempt = client.search_request([x])
                assert False, f"Should have raised ValueError/TypeError for {x} as non string in list"
            except (TypeError, ValueError):
                pass
    
    # Checking the limit object for being a positive int
    for x in [-1, 1.4, [], "str", {}, None, True]:
        try:
            attempt = client.search_request(["brand_name"], limit=x)
            assert False, f"Should have raised ValueError/TypeError for {x} as limit"
        except (TypeError, ValueError):
            pass

    # check a correct input
    search_items = [client.generic_search("brand_name", "Advil")]
    result = client.search_request(search_items, limit=1)
    assert isinstance(result, dict)
    

def test_DLC_manual_request():
    client = Drug_Label_Client(API_KEY)
    # check everything manually
    try:
        result = client.manual_request("not-url")
        assert False, "Should have raised RequestException"
    except requests.exceptions.RequestException:
        pass

def test_drug_functions():
    # make a client and get some json prepped for drug testing
    client = Drug_Label_Client(API_KEY)
    search_items = [client.generic_search("brand_name", "Advil")]
    result = client.search_request(search_items, limit=1)

    # mess up initiating advil
    for x in [1, [], "str", None, True]:
        try:
            advil_drug = Drug(x, {})
            assert False, "Both inputs should be dictionary items"
        except (TypeError, ValueError):
            pass
        try:
            advil_drug = Drug({},x)
            assert False, "Both inputs should be dictionary items"
        except (TypeError, ValueError):
            pass
    
    # initiate valid advil
    advil_drug = Drug(result["meta"],result["results"][0])

    # testing the functions with no inputs and an expected return value
    assert advil_drug.get_name() == result["results"][0]["openfda"]["brand_name"][0]
    assert advil_drug.raw_drug() == result["results"][0]
    assert advil_drug.get_date() == result["meta"]["last_updated"]

    # testing the get_parameter function for invalid inputs
    for x in [1, [], {}, None, True]:
        try:
            advil_drug = advil_drug.get_parameter(x)
            assert False, "input should be dictionary items"
        except (TypeError, ValueError):
            pass
    
    # testing the get_parameter function against the name assumption and the list parsing properties
    for x in result["results"][0]:
        if x not in ["brand_name", "generic_name", "name", "substance_name", "openfda"]:
            value = advil_drug.get_parameter(x)
            expected = result["results"][0][x]
            if isinstance(expected, list) and expected:
                assert value == expected[0]
            else:
                assert value == expected

    # testing the drug_comprehensive and drug_overview function to ensure no issues
    comprehensive = advil_drug.drug_comprehensive()
    assert isinstance(comprehensive, dict)
    assert len(comprehensive) > 0
    assert isinstance(advil_drug.drug_overview(), dict)

def test_shelf_functions():
    # initiate valid advil and Oxycodone    
    client = Drug_Label_Client(API_KEY)
    search_items = [client.generic_search("brand_name", "Advil")]
    result = client.search_request(search_items, limit=1)
    search_items_1 = [client.generic_search("brand_name", "Oxycodone")]
    result1 = client.search_request(search_items_1, limit=1)
    advil_drug = Drug(result["meta"],result["results"][0])
    oxy_drug = Drug(result1["meta"],result1["results"][0])
    
    # pass the wrong shelf capacity style
    for x in [-1, 1.4, [], {}, None, True]:
        try:
            my_shelf = Shelf(x)
            assert False, "input should be an integer for shelf capacity"
        except (TypeError, ValueError):
            pass

    # create valid shelf and validate
    my_shelf = Shelf(5)
    assert my_shelf.capacity == 5
    assert len(my_shelf.corelist) == 0

    # test wrong inputs for add_drug 
    for x in [-1, 1.4, [], {}, "string", None, True]:
        try:
            my_shelf.add_drug(x)
            assert False, "input should be a Drug object for add_drug"
        except (TypeError, ValueError):
            pass
        if not isinstance(x, str):
            try:
                my_shelf.add_drug(x)
                assert False, "input should be a string of the drug name"
            except (TypeError, ValueError):
                pass

    # add some drugs and test that everything works
    my_shelf.add_drug(advil_drug)
    assert len(my_shelf.corelist) == 1
    assert my_shelf.corelist[0].get_name() == result["results"][0]["openfda"]["brand_name"][0]
    my_shelf.add_drug(oxy_drug)
    assert len(my_shelf.corelist) == 2
    assert my_shelf.corelist[1].get_name() == result1["results"][0]["openfda"]["brand_name"][0]

    # wrong inputs for remove drug
    for x in [-1, 1.4, [], {}, None, True]:
        try:
            my_shelf.remove_drug(x)
            assert False, "input should be a string for remove_drug"
        except (TypeError, ValueError):
            pass
    
    # test removing either of the drugs 
    my_shelf_other = Shelf(5)
    my_shelf_other.add_drug(advil_drug)
    my_shelf_other.add_drug(oxy_drug)

    # remove now
    my_shelf.remove_drug(result1["results"][0]["openfda"]["brand_name"][0])
    assert len(my_shelf.corelist) == 1

    # test get_drugs
    assert isinstance(my_shelf.get_drugs(), list)

    # check shelf_stats output
    empty_shelf = Shelf(1)
    empty_shelf = Shelf(capacity=10)
    stats = empty_shelf.shelf_stats()

    # check empty outputs
    assert isinstance(stats, dict)
    assert stats["newest_drug"] is None
    assert stats["average_risk_score"] is None
    assert stats["average_total_fields"] is None
    assert stats["percentage_full"] == 0

    # check full stats
    fullstats = my_shelf.shelf_stats()
    assert isinstance(fullstats, dict)

    # check field_list and criteria_list
    for x in [-1, 1.4, "string", {}, None, True]:
        try:
            make_drugs(API_KEY, x, [])
            assert False, "input should be a list for field_list"
        except (TypeError, ValueError):
            pass
        try:
            make_drugs(API_KEY, [],x)
            assert False, "input should be a list for item_list"
        except (TypeError, ValueError):
            pass

    # compare lengths
    try:
        make_drugs(API_KEY, ["one"],["one","two"])
        assert False, "item_list and field_list must be identical in length"
    except (TypeError, ValueError):
        pass

    # check exact value:
    for x in [-1, 1.4, "string", {}, None]:
        try:
            make_drugs(API_KEY, ["hello"],["hello"],x)
            assert False, "input should be bool for exact"
        except (TypeError, ValueError):
            pass
    
    # check limit value:
    for x in [1.4, "string", {}, None]:
        try:
            make_drugs(API_KEY, ["hello"],["hello"],True,x)
            assert False, "input should be int for limit"
        except (TypeError, ValueError):
            pass

    # check correct input
    item = make_drugs(API_KEY, ["brand_name"],["Advil"])
    assert isinstance(item, list)