import structlog
def get_logger():
    structlog.configure(wrapper_class=structlog.make_filtering_bound_logger(20))
    return structlog.get_logger()
