import json
import os
import uuid

import graphviz
import matplotlib.pyplot as plt
import networkx as nx
from wordcloud import WordCloud

from agentd.utils import get_cloud_storage, get_generated_directory


def gen_random_id():
    return str(uuid.uuid1())[:6]


dummy_visualization_data = {
    "pie_chart_segments": [
        {"Health-Conscious Millennials": 40},
        {"Busy Professionals": 30},
        {"Fitness Enthusiasts": 20},
        {"Niche Segment": 10},
    ],
    "pain_points_bar_chart_data": [
        {"Lack of Time": 75},
        {"Lack of Motivation": 60},
        {"Conflicting Advice": 40},
        {"Cost": 25},
    ],
    "word_cloud_text": "health fitness app workout personalized nutrition goals tracking motivation busy parents professionals millennials technology convenience",
    "knowledge_graph_elements": {
        "nodes": [
            {"id": "persona_anna", "label": "Busy Anna", "type": "persona"},
            {"id": "problem_time", "label": "Lack of Time", "type": "problem"},
            {"id": "solution_quick", "label": "Quick Workouts", "type": "solution"},
            {
                "id": "segment_health",
                "label": "Health-Conscious Millennials",
                "type": "segment",
            },
        ],
        "edges": [
            {
                "source": "persona_anna",
                "target": "problem_time",
                "label": "experiences",
            },
            {
                "source": "solution_quick",
                "target": "problem_time",
                "label": "addresses",
            },
            {
                "source": "persona_anna",
                "target": "segment_health",
                "label": "belongs_to",
            },
        ],
    },
}


def save_diagram_to_file(figure, filename):
    """
    Saves a diagram to a local file and uploads it to cloud storage and returns the public URL.
    """
    output_dir = os.path.join(get_generated_directory(), "diagrams")
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, filename)

    # save locally

    if hasattr(figure, "savefig"):
        figure.savefig(file_path)

    elif isinstance(figure, graphviz.Digraph):
        # Render to PNG, cleanup source dot file
        # graphviz automatically adds extension
        file_path = file_path.removesuffix(".png")
        figure.render(file_path, format="png", cleanup=True)
        file_path += ".png"

    elif isinstance(figure, WordCloud):
        figure.to_file(file_path)

    else:
        raise ValueError(
            "Unsupported figure type. Must be a matplotlib Figure or graphviz Digraph."
            + " got "
            + str(type(figure))
        )

    print(f"Diagram saved to {file_path}")

    # upload to cloud storage
    print("Uploading diagram to cloud storage...")
    remote_file_path = os.path.join("diagrams", os.path.basename(file_path))
    if not remote_file_path.endswith(".png"):
        remote_file_path += ".png"
    get_cloud_storage().upload_file(local_path=file_path, remote_path=remote_file_path)
    print("Diagram uploaded to cloud storage.")
    os.remove(file_path)  # Clean up local file after upload
    # generate public URL
    print("Generating public URL for the diagram...")
    public_url = get_cloud_storage().get_file_url(remote_file_path)
    print(f"Public URL for the diagram: {public_url}")

    return public_url


def generate_diagrams(visualization_data=dummy_visualization_data):
    output_dir = os.path.join(get_generated_directory(), "diagrams")
    os.makedirs(output_dir, exist_ok=True)
    print("Generating diagrams for visualization data...")

    public_urls = {}

    # ==== Pie Chart: User Segments ====
    segment_data = visualization_data.get("pie_chart_segments")
    if segment_data:
        labels = [list(d.keys())[0] for d in segment_data]
        values = [list(d.values())[0] for d in segment_data]

        plt.figure(figsize=(8, 8))
        plt.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
        plt.title("Distribution of Identified User Segments")
        # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.axis("equal")
        plt.tight_layout()
        pie_chart_file_name = f"user_segments_pie_chart_{gen_random_id()}.png"
        public_url = save_diagram_to_file(plt, pie_chart_file_name)
        public_urls["pie_chart"] = public_url
        plt.close()  # Close the plot to free memory

    # === Bar Graph: Top Pain Points ===
    pain_point_data = visualization_data.get("pain_points_bar_chart_data")
    if pain_point_data:
        # Sort data for better visualization
        pain_point_data.sort(key=lambda x: list(x.values())[0], reverse=True)
        labels = [list(d.keys())[0] for d in pain_point_data]
        values = [list(d.values())[0] for d in pain_point_data]

        plt.figure(figsize=(10, 6))
        plt.barh(labels, values, color="skyblue")
        plt.xlabel("Frequency / Importance Score")
        plt.title("Identified User Pain Points")
        plt.gca().invert_yaxis()  # Put highest value at the top
        plt.tight_layout()

        bar_chart_file_name = f"user_pain_points_bar_chart_{gen_random_id()}.png"
        public_url = save_diagram_to_file(plt, bar_chart_file_name)
        public_urls["bar_chart"] = public_url

        plt.close()

    # === Word Cloud Generation ===
    word_cloud_text = visualization_data.get("word_cloud_text")
    if word_cloud_text:
        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color="white",
            max_words=100,
            collocations=False,
        ).generate(
            word_cloud_text
        )  # collocations=False for more distinct words
        word_cloud_file_name = f"target_audience_word_cloud_{gen_random_id()}.png"
        public_url = save_diagram_to_file(wordcloud, word_cloud_file_name)
        public_urls["word_cloud"] = public_url

    # === Knowledge Graph Visualization ===
    kg_data = visualization_data.get("knowledge_graph_elements")
    if kg_data and kg_data.get("nodes") and kg_data.get("edges"):
        dot = graphviz.Digraph(
            comment="Knowledge Graph", graph_attr={"rankdir": "LR"}
        )  # LR = Left to Right

        for node in kg_data["nodes"]:
            if node.get("type") == "persona":
                dot.node(
                    node["id"],
                    node["label"],
                    shape="box",
                    style="filled",
                    fillcolor="#ADD8E6",
                )  # Light Blue
            elif node.get("type") == "problem":
                dot.node(
                    node["id"],
                    node["label"],
                    shape="ellipse",
                    style="filled",
                    fillcolor="#FFD700",
                )  # Gold
            elif node.get("type") == "solution":
                dot.node(
                    node["id"],
                    node["label"],
                    shape="parallelogram",
                    style="filled",
                    fillcolor="#90EE90",
                )  # Light Green
            elif node.get("type") == "segment":
                dot.node(
                    node["id"],
                    node["label"],
                    shape="folder",
                    style="filled",
                    fillcolor="#FFB6C1",
                )  # Light Pink
            else:
                dot.node(node["id"], node["label"])  # Default

        # Add edges
        for edge in kg_data["edges"]:
            dot.edge(edge["source"], edge["target"], label=edge.get("label", ""))

        # Graphviz adds extension
        kg_file_name = f"knowledge_graph_{gen_random_id()}"
        public_url = save_diagram_to_file(dot, kg_file_name)
        public_urls["knowledge_graph"] = public_url

    return public_urls
