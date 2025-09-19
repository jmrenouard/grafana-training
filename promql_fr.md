# **Aide-mémoire Prometheus**

* [Aide-mémoire Prometheus](https://www.google.com/search?q=%23aide-m%C3%A9moire-prometheus)  
  * [Concepts de Base](https://www.google.com/search?q=%23concepts-de-base)  
  * [Exemples Choisis](https://www.google.com/search?q=%23exemples-choisis)  
  * [Questions et Réponses](https://www.google.com/search?q=%23questions-et-r%C3%A9ponses)  
  * [Exemples de Requêtes](https://www.google.com/search?q=%23exemples-de-requ%C3%AAtes)  
  * [Configuration du Scrape](https://www.google.com/search?q=%23configuration-du-scrape)  
  * [Grafana avec Prometheus](https://www.google.com/search?q=%23grafana-avec-prometheus)  
    * [Variables](https://www.google.com/search?q=%23variables)  
  * [Règles d'Enregistrement (Recording Rules)](https://www.google.com/search?q=%23r%C3%A8gles-denregistrement-recording-rules)  
  * [Instrumentation d'Application](https://www.google.com/search?q=%23instrumentation-dapplication)  
    * [Python Flask](https://www.google.com/search?q=%23python-flask)  
  * [Sources Externes](https://www.google.com/search?q=%23sources-externes)

## **Concepts de Base**

* Counter (Compteur) : Une métrique de type compteur ne fait qu'augmenter.  
* Gauge (Jauge) : Une métrique de type jauge peut augmenter ou diminuer.  
* Histogram (Histogramme) : Une métrique de type histogramme peut augmenter ou diminuer.  
* [Source et Statistiques 101](https://opensource.com/article/18/4/metrics-monitoring-and-python)

Fonctions de Requête :

* rate - La fonction rate calcule le taux d'augmentation par seconde d'un compteur sur une fenêtre de temps donnée. [src](https://levelup.gitconnected.com/prometheus-counter-metrics-d6c393d86076)  
* irate - Calcule le taux d'augmentation par seconde d'un compteur sur une fenêtre de temps définie. La différence est que irate ne regarde que les deux derniers points de données. Cela rend irate bien adapté pour graphiquer des compteurs volatiles et/ou rapides. [src](https://levelup.gitconnected.com/prometheus-counter-metrics-d6c393d86076)  
* increase - La fonction increase calcule l'augmentation d'un compteur sur une période de temps donnée. [src](https://levelup.gitconnected.com/prometheus-counter-metrics-d6c393d86076)  
* resets - La fonction donne le nombre de réinitialisations (resets) du compteur sur une fenêtre de temps donnée. [src](https://levelup.gitconnected.com/prometheus-counter-metrics-d6c393d86076)

## **Exemples Choisis**

Exemples de requêtes par exportateur / service :

* [Métriques Node Exporter](https://www.google.com/search?q=metric_examples/NODE_METRICS.md)

## **Questions et Réponses**

Comment puis-je obtenir le nombre de requêtes sur une période donnée (la période du dashboard) :



sum by (uri) (increase(http_requests_total[$__range ]))

Combien de redémarrages de pod par minute ?



rate(kube_pod_container_status_restarts_total{job="kube-state-metrics",namespace="default"}[15m]) * 60 * 15

## **Exemples de Requêtes**

Montre-moi tous les noms de métriques pour le job=app :



group ({job="app"}) by (__name__)

Combien de nœuds sont démarrés (up) ?



up

Combiner les valeurs de 2 vecteurs différents (Nom d'hôte avec une métrique) :



up * on(instance) group_left(nodename) (node_uname_info)

Exclure des labels :



sum without(job) (up * on(instance)  group_left(nodename)  (node_uname_info))

Compter les cibles (targets) par job :



count by (job) (up)

Quantité de mémoire disponible :



node_memory_MemAvailable_bytes

Quantité de mémoire disponible en Mo :



node_memory_MemAvailable_bytes/1024/1024

Quantité de mémoire disponible en Mo il y a 10 minutes :



node_memory_MemAvailable_bytes/1024/1024 offset 10m

Moyenne de la mémoire disponible sur les 5 dernières minutes :



avg_over_time(node_memory_MemAvailable_bytes[5m])/1024/1024

Utilisation de la mémoire en pourcentage :



100 * (1 - ((avg_over_time(node_memory_MemFree_bytes[10m]) + avg_over_time(node_memory_Cached_bytes[10m]) + avg_over_time(node_memory_Buffers_bytes[10m])) / avg_over_time(node_memory_MemTotal_bytes[10m])))

Utilisation du CPU :



100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle", instance="my-instance"}[5m])) * 100 )

Utilisation du CPU avec un décalage de 24 heures :



100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle", instance="my-instance"}[5m] offset 24h)) * 100 )

Utilisation du CPU par cœur :



( (1 - rate(node_cpu_seconds_total{job="node-exporter", mode="idle", instance="$instance"}[$__interval])) / ignoring(cpu) group_left count without (cpu)( node_cpu_seconds_total{job="node-exporter", mode="idle", instance="$instance"}) )

Utilisation du CPU par nœud :



100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[10m]) * 100\) * on(instance) group_left(nodename) (node_uname_info))

Mémoire disponible par nœud :



node_memory_MemAvailable_bytes * on(instance) group_left(nodename) (node_uname_info)

Ou si vous dépendez des labels d'autres métriques :



(node_memory_MemTotal_bytes{job="node-exporter"} - node_memory_MemFree_bytes{job="node-exporter"} - node_memory_Buffers_bytes{job="node-exporter"} - node_memory_Cached_bytes{job="node-exporter"}) * on(instance) group_left(nodename) (node_uname_info{nodename=~"$nodename"})

Charge moyenne (Load Average) en pourcentage :



avg(node_load1{instance=~"$name", job=~"$job"}) /  count(count(node_cpu_seconds_total{instance=~"$name", job=~"$job"}) by (cpu)) * 100

Charge moyenne par instance :



sum(node_load5{}) by (instance) / count(node_cpu_seconds_total{mode="user"}) by (instance) * 100

Charge moyenne (moyenne par instance_id : disons que la métrique a 2 valeurs de label identiques mais qui sont différentes) :



avg by (instance_id, instance) (node_load1{job=~"node-exporter", aws_environment="dev", instance="debug-dev"})  
# {instance="debug-dev",instance_id="i-aaaaaaaaaaaaaaaaa"}  
# {instance="debug-dev",instance_id="i-bbbbbbbbbbbbbbbbb"}

Disque disponible par nœud :



node_filesystem_free_bytes{mountpoint="/"} * on(instance) group_left(nodename) (node_uname_info)

IO Disque par nœud : Sortant :



sum(rate(node_disk_read_bytes_total[1m])) by (device, instance) * on(instance) group_left(nodename) (node_uname_info)

IO Disque par nœud : Entrant :



sum(rate(node_disk_written_bytes_total{job="node"}[1m])) by (device, instance) * on(instance) group_left(nodename) (node_uname_info)

IO Réseau par nœud :



sum(rate(node_network_receive_bytes_total[1m])) by (device, instance) * on(instance) group_left(nodename) (node_uname_info)  
sum(rate(node_network_transmit_bytes_total[1m])) by (device, instance) * on(instance) group_left(nodename) (node_uname_info)

Redémarrages de processus :



changes(process_start_time_seconds{job=~".+"}[15m])

Rotation de conteneurs (Cycling) :



(time() - container_start_time_seconds{job=~".+"}) \< 60

Histogramme :



histogram_quantile(1.00, sum(rate(prometheus_http_request_duration_seconds_bucket[5m])) by (handler, le)) * 1e3

Métriques d'il y a 24 heures (utile pour comparer aujourd'hui avec hier) :



# requête a  
total_number_of_errors{instance="my-instance", region="eu-west-1"}  

# requête b  
total_number_of_errors{instance="my-instance", region="eu-west-1"} offset 24h

# en lien :  
# https://about.gitlab.com/blog/2019/07/23/anomaly-detection-using-prometheus/

Nombre de nœuds (Up) :



count(up{job="cadvisor_my-swarm"})

Conteneurs en cours d'exécution par nœud :



count(container_last_seen) BY (container_label_com_docker_swarm_node_id)

Conteneurs en cours d'exécution par nœud, inclure les noms d'hôte correspondants :



count(container_last_seen) BY (container_label_com_docker_swarm_node_id) * ON (container_label_com_docker_swarm_node_id) GROUP_LEFT(node_name) node_meta

Codes de réponse HAProxy :



haproxy_server_http_responses_total{backend=~"$backend", server=~"$server", code=~"$code", alias=~"$alias"} \> 0

Métriques avec le plus de ressources :



topk(10, count by (__name__)({__name__=~".+"}))

la même chose, mais par job :



topk(10, count by (__name__, job)({__name__=~".+"}))

ou les jobs qui ont le plus de séries temporelles :



topk(10, count by (job)({__name__=~".+"}))

Top 5 par valeur :



sort_desc(topk(5, aws_service_costs))

Tableau - Top 5 (activer aussi l'instantané) :



sort(topk(5, aws_service_costs))

Le plus de métriques par job, trié :



sort_desc (sum by (job) (count by (__name__, job)({job=~".+"})))

Grouper par jour (Tableau) - en cours



aws_service_costs{service=~"$service"} \+ ignoring(year, month, day) group_right  
  count_values without() ("year", year(timestamp(  
    count_values without() ("month", month(timestamp(  
      count_values without() ("day", day_of_month(timestamp(  
        aws_service_costs{service=~"$service"}  
      )))  
    )))  
  ))) * 0

Grouper les métriques par nom d'hôte du nœud :



node_memory_MemAvailable_bytes * on(instance) group_left(nodename) (node_uname_info)

..  
{cloud_provider="amazon",instance="x.x.x.x:9100",job="node_n1",my_hostname="n1.x.x",nodename="n1.x.x"}

Soustraire deux métriques de type jauge (exclure le label qui ne correspond pas) :



polkadot_block_height{instance="polkadot", chain=~"$chain", status="sync_target"} - ignoring(status) polkadot_block_height{instance="polkadot", chain=~"$chain", status="finalized"}

Moyenne CPU des conteneurs sur 5m :



(sum by(instance, container_label_com_amazonaws_ecs_container_name, container_label_com_amazonaws_ecs_cluster) (rate(container_cpu_usage_seconds_total[5m])) * 100\)

Utilisation mémoire des conteneurs : Total :



sum(container_memory_rss{container_label_com_docker_swarm_task_name=~".+"})

Mémoire des conteneurs, par Tâche, Nœud :



sum(container_memory_rss{container_label_com_docker_swarm_task_name=~".+"}) BY (container_label_com_docker_swarm_task_name, container_label_com_docker_swarm_node_id)

Mémoire des conteneurs par Nœud :



sum(container_memory_rss{container_label_com_docker_swarm_task_name=~".+"}) BY (container_label_com_docker_swarm_node_id)

Utilisation mémoire par Stack :



sum(container_memory_rss{container_label_com_docker_swarm_task_name=~".+"}) BY (container_label_com_docker_stack_namespace)

Supprimer des résultats les métriques qui ne contiennent pas un label spécifique :



container_cpu_usage_seconds_total{container_label_com_amazonaws_ecs_cluster\!=""}

Supprimer des labels d'une métrique :



sum without (age, country) (people_metrics)

Voir les 10 plus grosses métriques par nom :



topk(10, count by (__name__)({__name__=~".+"}))

Voir les 10 plus grosses métriques par nom, job :



topk(10, count by (__name__, job)({__name__=~".+"}))

Voir toutes les métriques pour un job spécifique :



{__name__=~".+", job="node-exporter"}

Voir toutes les métriques pour plusieurs jobs en utilisant les sélecteurs de vecteurs



{__name__=~".+", job=~"traefik|cadvisor|prometheus"}

Disponibilité (uptime) d'un site web avec blackbox-exporter :



# https://www.robustperception.io/what-percentage-of-time-is-my-service-down-for

avg_over_time(probe_success{job="node"}[15m]) * 100

Supprimer / Remplacer :

* [https://medium.com/@texasdave2/replace-and-remove-a-label-in-a-prometheus-query-9500faa302f0](https://medium.com/@texasdave2/replace-and-remove-a-label-in-a-prometheus-query-9500faa302f0)

Nombre de requêtes client :



irate(http_client_requests_seconds_count{job="web-metrics", environment="dev", uri\!~".*actuator.*"}[5m])

Temps de réponse client :



irate(http_client_requests_seconds_sum{job="web-metrics", environment="dev", uri\!~".*actuator.*"}[5m]) /  
irate(http_client_requests_seconds_count{job="web-metrics", environment="dev", uri\!~".*actuator.*"}[5m])

Requêtes par seconde :



sum(increase(http_server_requests_seconds_count{service="my-service", env="dev"}[1m])) by (uri)

est identique à :



sum(rate(http_server_requests_seconds_count{service="my-service", env="dev"}[1m]) * 60 ) by (uri)

Voir [ce fil Stack Overflow](https://stackoverflow.com/questions/66282512/grafana-graphing-http-requests-per-minute-with-http-server-requests-seconds-coun) pour plus de détails.

Requêtes et limites de ressources :



# pour le cpu : taux moyen d'utilisation du cpu sur 15 minutes  
rate(container_cpu_usage_seconds_total{job="kubelet",container="my-application"}[15m])

# pour la mémoire : affiche en Mo  
container_memory_usage_bytes{job="kubelet",container="my-application"}  / (1024 * 1024\)

## **Configuration du Scrape**

configurations de relabeling (relabel_configs) :

YAML

# exemple complet : https://gist.github.com/ruanbekker/72216bea59fc56af189f5a7b2e3a8002  
scrape_configs:  
  - job_name: 'multipass-nodes'  
    static_configs:  
    - targets: ['ip-192-168-64-29.multipass:9100']  
      labels:  
        env: test  
    - targets: ['ip-192-168-64-30.multipass:9100']  
      labels:  
        env: test  
    # https://grafana.com/blog/2022/03/21/how-relabeling-in-prometheus-works/#internal-labels  
    relabel_configs:  
    - source_labels: [__address__]  
      separator: ':'  
      regex: '(.*):(.*)'  
      replacement: '${1}'  
      target_label: instance

configurations statiques (static_configs) :

YAML

scrape_configs:  
  - job_name: 'prometheus'  
    scrape_interval: 5s  
    static_configs:  
        - targets: ['localhost:9090']  
      labels:  
        region: 'eu-west-1'

configurations de découverte de service DNS (dns_sd_configs) :

YAML

scrape_configs:  
  - job_name: 'mysql-exporter'  
    scrape_interval: 5s  
    dns_sd_configs:  
    - names:  
      - 'tasks.mysql-exporter'  
      type: 'A'  
      port: 9104  
    relabel_configs:  
    - source_labels: [__address__]  
      regex: '.*'  
      target_label: instance  
      replacement: 'mysqld-exporter'

Liens utiles :

* [https://gist.github.com/ruanbekker/72216bea59fc56af189f5a7b2e3a8002](https://gist.github.com/ruanbekker/72216bea59fc56af189f5a7b2e3a8002)  
* [https://gist.github.com/trastle/1aa205354577ef0b329d4b8cc84c674a](https://gist.github.com/trastle/1aa205354577ef0b329d4b8cc84c674a)  
* [https://github.com/prometheus/docs/issues/341](https://github.com/prometheus/docs/issues/341)  
* [https://medium.com/quiq-blog/prometheus-relabeling-tricks-6ae62c56cbda](https://medium.com/quiq-blog/prometheus-relabeling-tricks-6ae62c56cbda)  
* [https://blog.freshtracks.io/prometheus-relabel-rules-and-the-action-parameter-39c71959354a](https://blog.freshtracks.io/prometheus-relabel-rules-and-the-action-parameter-39c71959354a)  
* [https://www.robustperception.io/relabel_configs-vs-metric_relabel_configs](https://www.robustperception.io/relabel_configs-vs-metric_relabel_configs)  
* [https://training.robustperception.io/courses/prometheus-configuration/lectures/3170347](https://training.robustperception.io/courses/prometheus-configuration/lectures/3170347)

## **Grafana avec Prometheus**

Si vous avez une sortie comme celle-ci dans Grafana :

{instance="10.0.2.66:9100",job="node",nodename="rpi-02"}

et que vous voulez seulement afficher les noms d'hôte, vous pouvez appliquer ce qui suit dans le champ "Legend" (Légende) :

{{nodename}}

Si votre sortie veut exported_instance dans :



sum(exporter_memory_usage{exported_instance="myapp"})

Vous devriez faire :



sum by (exported_instance) (exporter_memory_usage{exported_instance="my_app"})

Puis dans la Légende :

{{exported_instance}}

### **Variables**

* Nom d'hôte (Hostname) :

name: node  
label: node  
node: label_values(node_uname_info, nodename)  
Ensuite dans Grafana vous pouvez utiliser :



sum(rate(node_disk_read_bytes_total{job="node"}[1m])) by (device, instance) * on(instance) group_left(nodename) (node_uname_info{nodename=~"$node"})

* Adresse du Node Exporter

type: query  
query: label_values(node_network_up, instance)

* Adresse du MySQL Exporter

type: query  
query: label_values(mysql_up, instance)

* Valeurs statiques :

type: custom  
name: dc  
label: dc  
values seperated by comma: eu-west-1a,eu-west-1b,eu-west-1c

* Noms de Stack Docker Swarm

name: stack  
label: stack  
query: label_values(container_last_seen,container_label_com_docker_stack_namespace)

* Noms de Service Docker Swarm

name: service_name  
label: service_name  
query: label_values(container_last_seen,container_label_com_docker_swarm_service_name)

* ID de Nœud Manager Docker Swarm :

name: manager_node_id  
label: manager_node_id  
query:

label_values(container_last_seen{container_label_com_docker_swarm_service_name=~"proxy_traefik", container_label_com_docker_swarm_node_id=~".*"}, container_label_com_docker_swarm_node_id)

* Stacks Docker Swarm tournant sur les Managers

name: stack_on_manager  
label: stack_on_manager  
query:

label_values(container_last_seen{container_label_com_docker_swarm_node_id=~"$manager_node_id"},container_label_com_docker_stack_namespace)

## **Règles d'Enregistrement (Recording Rules)**

* [L'article sur les Recording Rules de @deploy.live](https://deploy.live/blog/today-i-learned-prometheus-recording-rules/)

## **Instrumentation d'Application**

### **Python Flask**

* [@ramdesh flask-prometheus-grafana-example](https://github.com/ramdesh/flask-prometheus-grafana-example)

## **Sources Externes**

* [Prometheus](https://prometheus.io/docs/querying/basics/)  
* [PromQL pour les débutants](https://medium.com/@valyala/promql-tutorial-for-beginners-9ab455142085)  
* [Prometheus 101](https://medianetlab.gr/prometheus-101/)  
* [Section.io: Requêtes Prometheus](https://www.section.io/blog/prometheus-querying/)  
* [InnoQ: Compteurs Prometheus](https://www.innoq.com/en/blog/prometheus-counters/)  
* [Les plus grosses métriques](https://www.robustperception.io/which-are-my-biggest-metrics)  
* [Top des métriques](https://github.com/grafana/grafana/issues/6561)  
* [Ordina-Jworks](https://ordina-jworks.github.io/monitoring/2016/09/23/Monitoring-with-Prometheus.html)  
* [Infinity Works](https://github.com/infinityworks/prometheus-example-queries)  
* [Astuces de Relabeling Prometheus](https://medium.com/quiq-blog/prometheus-relabeling-tricks-6ae62c56cbda)  
* [@Valyala: Tutoriel PromQL pour les débutants](https://medium.com/@valyala/promql-tutorial-for-beginners-9ab455142085)  
* [@Jitendra: Aide-mémoire PromQL](https://github.com/jitendra-1217/promql.cheat.sheet)  
* [InfinityWorks: Exemples de requêtes Prometheus](https://github.com/infinityworks/prometheus-example-queries/blob/master/README.md)  
* [Timber: PromQL pour les humains](https://timber.io/blog/promql-for-humans/)  
* [SectionIO: Requêtes Prometheus](https://www.section.io/blog/prometheus-querying/)  
* [RobustPerception](https://www.google.com/search?q)  
  * [RobustPerception: Comprendre l'utilisation CPU d'une machine](https://www.robustperception.io/understanding-machine-cpu-usage)  
  * [RobustPerception: Patterns de requêtes courants en PromQL](https://www.robustperception.io/common-query-patterns-in-promql)  
  * [RobustPerception: Disponibilité de site web](https://www.robustperception.io/what-percentage-of-time-is-my-service-down-for)  
  * [RobustPerception: Comment fonctionne un histogramme Prometheus](https://www.robustperception.io/how-does-a-prometheus-histogram-work)  
  * [RobustPerception: Comment fonctionne un compteur Prometheus](https://www.robustperception.io/how-does-a-prometheus-counter-work)  
  * [RobustPerception: Comment fonctionne une jauge Prometheus](https://www.robustperception.io/how-does-a-prometheus-gauge-work)  
  * [RobustPerception: Comment fonctionne un sommaire Prometheus](https://www.robustperception.io/how-does-a-prometheus-summary-work)  
* [DevConnected: Le guide définitif de Prometheus](https://devconnected.com/the-definitive-guide-to-prometheus-in-2019/)  
* [@showmax Introduction à Prometheus](https://tech.showmax.com/2019/10/prometheus-introduction/)  
* [@rancher Monitoring de Cluster](https://rancher.com/docs/rancher/v2.0-v2.4/en/cluster-admin/tools/cluster-monitoring/expression/)  
* [Statistiques CPU de Prometheus](https://utcc.utoronto.ca/~cks/space/blog/sysadmin/PrometheusCPUStats)  
* [@aws Règles de réécriture Prometheus pour k8s](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/ContainerInsights-Prometheus-Setup-configure.html#ContainerInsights-Prometheus-Setup-config-scrape)  
* [ec2_sd_configs](https://www.google.com/search?q)  
  * [Prometheus AWS Cross Account ec2_sd_config](https://jarodw.com/posts/prometheus-ec2-sd-multiple-aws-accounts/)  
  * [Rôle pour Prometheus AWS ec2_sd_config](https://medium.com/investing-in-tech/automatic-monitoring-for-all-new-aws-instances-using-prometheus-service-discovery-97d37a5b2ea2)  
* [kubernetes_sd_configs](https://www.google.com/search?q)  
  * [fabianlee configurations kubernetes](https://fabianlee.org/2022/07/08/prometheus-monitoring-services-using-additional-scrape-config-for-prometheus-operator/)  
* @metricfire.com: Comprendre la fonction Rate  
  Dashboards :  
* [Alerter sur les labels et métriques manquants](https://niravshah2705.medium.com/prometheus-alert-for-missing-metrics-and-labels-afd4b8f12b1)  
* [@devconnected Dashboard pour les I/O disque](https://devconnected.com/monitoring-disk-i-o-on-linux-with-the-node-exporter/)  
* [@deploy.live règles d'enregistrement](https://deploy.live/blog/today-i-learned-prometheus-recording-rules/)  
* [Requêtes CPU et mémoire](https://gist.github.com/max-rocket-internet/6a05ee757b6587668a1de8a5c177728b)  
* [Métriques de type compteur Prometheus](https://levelup.gitconnected.com/prometheus-counter-metrics-d6c393d86076)

Configurations :

* [Simuler les tags AWS dans un Prometheus local](https://ops.tips/blog/simulating-aws-tags-in-local-prometheus/)