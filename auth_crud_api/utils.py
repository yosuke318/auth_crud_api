from typing import Any, Dict


def pre_token_generate(event: Dict[str, Any], prefix: str) -> Dict[str, Any]:
    """
    トークン生成前に、prefix付きのuuidをIDトークンに追加します
    :param event:
    :type event:
    :param prefix:
    :type prefix:
    :rtype: Dict
    """

    try:
        event['response']['claimsOverrideDetails'] = {
            'claimsToAddOrOverride': {
                'prefixed_sub': prefix + '_' + event['request']['userAttributes']['sub']
            }
        }
        return event

    except Exception as e:
        print(f"Pre token generate failed: {e}")
        raise