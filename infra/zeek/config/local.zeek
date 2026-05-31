@load base/frameworks/logging
@load base/protocols/conn
@load base/protocols/http
@load zeek-http-log

redef Log::disable_stream(Conn::LOG);
redef Log::disable_stream(HTTP::LOG);

redef Log::enable_stream(HTTPLog::LOG);
