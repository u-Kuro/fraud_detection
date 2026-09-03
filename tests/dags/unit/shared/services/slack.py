from dags.shared.services.slack import create_blocks, slack_client

def test_create_blocks_returns_list():
    blocks = create_blocks(title="Hello", body="World")
    assert isinstance(blocks, list)

def test_create_blocks_has_header():
    blocks = create_blocks(title="My Title", body="Body text")
    header = next(b for b in blocks if b.get("type") == "header")
    assert header["text"]["text"] == "My Title"

def test_create_blocks_has_section():
    blocks = create_blocks(title="T", body="Body content")
    section = next(b for b in blocks if b.get("type") == "section")
    assert section["text"]["text"] == "Body content"

def test_create_blocks_with_buttons_includes_actions():
    buttons = [{"type": "button", "text": {"type": "plain_text", "text": "OK"}}]
    blocks = create_blocks(title="T", body="B", buttons=buttons)
    actions = [b for b in blocks if b.get("type") == "actions"]
    assert len(actions) == 1

def test_create_blocks_without_buttons_has_no_actions():
    blocks = create_blocks(title="T", body="B")
    actions = [b for b in blocks if b.get("type") == "actions"]
    assert len(actions) == 0

def test_slack_client_is_not_none():
    assert slack_client is not None
