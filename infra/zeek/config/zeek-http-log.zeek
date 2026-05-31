module HTTPLog;

export {
    redef record Conn::Info += {
        http_method: string &log &optional;
        http_path: string &log &optional;
        http_status: string &log &optional;
        http_user_agent: string &log &optional;
        http_host: string &log &optional;
        http_referrer: string &log &optional;
        http_response_size: count &log &optional;
    };
}

event http_request(c: connection, method: string, original_URI: string, unescaped_URI: string, version: string)
{
    c$http = HTTP::Info($ts = network_time());
    c$http$method = method;
    c$http$path = original_URI;
}

event http_reply(c: connection, version: string, status_code: count, reason: string)
{
    if (c?$http)
    {
        c$http$status_code = status_code;
    }
}

event http_header(c: connection, is_orig: bool, name: string, value: string)
{
    if (c?$http)
    {
        if (to_lower(name) == "user-agent")
            c$http$user_agent = value;
        if (to_lower(name) == "host")
            c$http$host = value;
        if (to_lower(name) == "referer")
            c$http$referrer = value;
    }
}

event http_endpoint(c: connection)
{
    if (c?$http)
    {
        c$http$response_size = c$http$resp_body_len;
    }
}
