import os,pytest
from app.tool_registry import is_registered
from app.config_validation import validate_production
def test_registry():
    assert is_registered("mone_search_customer")
    assert is_registered("mone_create_project")
    assert not is_registered("arbitrary_tool")
def test_config_contract(): assert isinstance(validate_production(),list)
@pytest.mark.skipif(os.getenv("RUN_EXTERNAL_INTEGRATION")!="1",reason="requires staging credentials")
def test_external_credentials():
    assert os.getenv("AI_API_KEY") and os.getenv("MONE_API_URL") and os.getenv("MONE_API_TOKEN")
