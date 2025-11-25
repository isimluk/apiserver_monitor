import time
from datetime import datetime
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
        try:
            v1.list_namespace(_request_timeout=3)
            if error_start:
                recovery_time = datetime.utcnow() - error_start
                log(f"RECOVERY: API server available after {recovery_time.total_seconds():.2f} seconds outage.")
                error_start = None
            else:
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

if __name__ == "__main__":
    main()