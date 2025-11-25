import time
from datetime import datetime, timedelta
from kubernetes import client, config
from kubernetes.client.rest import ApiException

def log(msg):
    print(f"[{datetime.utcnow().isoformat()}] {msg}", flush=True)

def main():
    # Try in-cluster config, fallback to kubeconfig
    try:
        config.load_incluster_config()
        log("Loaded in-cluster config.")
    except Exception:
        config.load_kube_config()
        log("Loaded kubeconfig.")

    v1 = client.CoreV1Api()
    error_start = None

    while True:
        start = datetime.utcnow()
        try:
            v1.list_namespace(_request_timeout=3)
            if error_start:
                recovery_time = datetime.utcnow() - error_start
                log(f"RECOVERY: API server available after {recovery_time.total_seconds():.2f} seconds outage.")
                error_start = None
            else:
                if start.second == 0:
                    log("API server OK")
        except Exception as e:
            if not error_start:
                error_start = datetime.utcnow()
                if isinstance(e, ApiException):
                    log(f"ERROR: kube-apiserver unavailable: status={e.status}, reason={e.reason}, body={e.body}")
                else:
                    log(f"ERROR: kube-apiserver unavailable: {repr(e)}")
            else:
                if isinstance(e, ApiException):
                    log(f"ERROR: still unavailable: status={e.status}, reason={e.reason}, body={e.body} (outage ongoing)")
                else:
                    log(f"ERROR: still unavailable: {repr(e)} (outage ongoing)")
        time.sleep(5)
        # Sleep until the top of the next second
        now = datetime.utcnow()
        next_second = (start + timedelta(seconds=1)).replace(microsecond=0)
        sleep_time = (next_second - now).total_seconds()
        if sleep_time > 0:
            time.sleep(sleep_time)

if __name__ == "__main__":
    main()
