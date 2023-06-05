import networkx as nx
import matplotlib.pyplot as plt


class VisualizerSitemap:

    def __init__(self, filename="visual_xml/filename.png"):
        self.filename = "visual_xml/" + filename

        self.graph = nx.DiGraph()

    def start_visualizer(self, urls_dict: dict) -> None:
        key = list(urls_dict.keys())[0]

        print("Waiting for sitemap visualizer...")

        self.graph = self.graph_bypass(self.graph, key, urls_dict[key])
        plt.figure(1, figsize=(15, 15))
        nx.draw(self.graph, node_size=30, font_size=8, with_labels=True)
        plt.savefig(self.filename, dpi=200)
        plt.show()

    @staticmethod
    def graph_bypass(graph: nx.Graph, parent: str, child: dict) -> nx.Graph:
        for key, val in child.items():
            node_child = key.split('/')[-1]
            node_parent = parent.split('/')[-1]

            if len(node_child) > 5:
                node_child = node_child[:5] + "..."

            if len(node_parent) > 5:
                node_parent = node_parent[:5] + "..."

            graph.add_edge(node_child, node_parent)
            graph = VisualizerSitemap.graph_bypass(graph, key, val)

        return graph


if __name__ == "__main__":

    test_dict = {"/some_url": {"/some_url/test": {}, "/some_url/foo": {"/some_url/foo/bar": {}}, "/some_url/go": {}}}

    sitemap_visual = VisualizerSitemap()
    sitemap_visual.start_visualizer(test_dict)
