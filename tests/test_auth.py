from napalm_logs.auth import NapalmLogsAuthProc


def start_fail():
    nlap = NapalmLogsAuthProc('/home/mircea/napalm-logs/examples/server.crt',
			  '/home/mircea/napalm-logs/examples/server.key',
			  'a',
			  'b',
			  None)
    nlap.start()
    nlap.stop()
