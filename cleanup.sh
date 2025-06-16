kubectl delete -f kubernetes/
minikube stop
minikube delete --all
eval $(minikube docker-env -u)

