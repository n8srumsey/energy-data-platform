
create or replace api integration github_integration
    api_provider = git_https_api
    api_allowed_prefixes = ('https://github.com/n8srumsey/energy-usage-reliability-data-platform.git')
    enabled = true
    allowed_authentication_secrets = all
    api_user_authentication = (type = snowflake_github_app ) -- enable OAuth support
    -- comment='<comment>';
