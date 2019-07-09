'''
Creates full-genome fasta files for each clusters.
'''
import os
import json
import argparse

'''
Load clusters into usable python dictionary
'''
def clusters(file, min_size):
    diction = {}
    with open(file) as jfile:
        json_data = json.load(jfile)
        for strain, cluster_dict in json_data["nodes"].items():
            cluster_number = cluster_dict['cluster']
            if cluster_number in diction:
                diction[cluster_number][strain] = []
            else:
                diction[cluster_number] = {strain : []}
    dict_scan = dict(diction)
    for cluster_id, cluster_strains in dict_scan.items():
        if len(cluster_strains) < min_size:
            del diction[cluster_id]
    return diction


'''
Adds sequences into python dictionary by cluster
'''
def sequences(clusters, files):
    for fname in files:
        with open(fname) as jfile:
            json_data = json.load(jfile)
            for cluster_id, cluster_strains in clusters.items():
                for strain in cluster_strains.keys():
                    if strain in json_data["nodes"].keys():
                        seq = json_data["nodes"][strain]["sequence"]
                        clusters[cluster_id][strain].append(seq)
    for cluster_id, cluster_strains in clusters.items():
        for strain, sequence in cluster_strains.items():
            clusters[cluster_id][strain] = ''.join(sequence)
    return clusters


'''
Outputs python dictionary sequences into fasta files
'''
def export_genomes(seq_dict, output_dir):
    for cluster, cluster_strains in seq_dict.items():
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        filename = output_dir + '/cluster' + str(cluster) + '.fasta'
        with open (filename, "w") as fasta:
            for strain, seq in cluster_strains.items():
                fasta.write('>' + strain + '\n' + seq + '\n')
    return fasta

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Create full-genome fasta files of clusters, output one FASTA per cluster",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument('--clusters', type = str, required = True, help = "cluster JSON files")
    parser.add_argument('--nt-muts', nargs = '+', type = str, required = True, help = "list of nt-muts JSON files")
    parser.add_argument('--min-size', type = int, default = 2, help = "Minimum number of strains in cluster. Default is 2.")
    parser.add_argument('--output-dir', type = str, required = True, help = "output directory")
    args = parser.parse_args()

    # Create clusters dictionary
    cluster_dict = clusters(args.clusters, args.min_size)

    # Makes sequences dictionary
    cluster_seq_dict = sequences(cluster_dict, args.nt_muts)

    # Outputs fasta files
    export_genomes(cluster_seq_dict, args.output_dir)