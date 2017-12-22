import os.path
import sys

import networkx as nx

script_path = os.path.realpath(__file__)
vimana_path = os.path.dirname(os.path.dirname(os.path.dirname(script_path)))
sys.path.append(vimana_path)

import vimana.photoscan_automation.photogrammetry_steps as pg_step
# import matplotlib.pyplot as plt

class WorkflowGraph:
    """
    Implements a standard workflow graph that the workflow can execute.

    Each step is a node in the graph.
    The relation between a step and next step is defined as an edge
    """

    def __init__(self, graph_name):
        self.G = nx.DiGraph(name=graph_name)
        self.graphName = graph_name
        self.start = None

    def add_workflow_step(self, step):
        if self.start is None:
            self.start = step
        self.G.add_node(step, name=str(step))

    def step_exists(self, step):
        return step in self.G.nodes()

    def add_next_step(self, step, next_step):
        self.G.add_edge(step, next_step)

    def get_next(self, step: object):
        for n in self.G.nodes():
            if n == step:
                if self.G.edges(n) is not None and len(self.G.edges(n)) > 0:
                    first_edge = self.G.edges(n)[0]
                    return first_edge[1]
                else:
                    return None

    def get_next_node_by_name(self,step):
        for n in self.G.nodes():
            if str(n) == step:
                if self.G.edges(n) is not None and len(self.G.edges(n)) > 0:
                    first_edge = self.G.edges(n)[0]
                    return first_edge[1]
                else:
                    return None


def default_photogrammetry_workflow_graph(workflow_object=None):
    """
    Creates the default photogrammetry workflow graph to be
    referenced by the workflow for execution.

    :return: WorkflowGraph object representing the default photogrammetry workflow.
    """

    add_photos = pg_step.AddPhotos(workflow_object)

    #extract_video_frames = pg_step.ExtractVideoFrames(workflow_object)
    check_camera_altitude = pg_step.CheckCameraAltitude(workflow_object)
    estimate_image_quality = pg_step.EstimateImageQuality(workflow_object)
    align_photos = pg_step.AlignPhotos(workflow_object)
    addGCPs = pg_step.AddGCPs(workflow_object)
    # detect_markers = pg_step.DetectMarkers(workflow_object)
    # check_marker_error = pg_step.CheckMarkerError(workflow_object)
    optimize_camera = pg_step.OptimizeCamera(workflow_object)
    bounding_box = pg_step.BoundingBox(workflow_object)
    split_into_chunk = pg_step.SplitChunks(workflow_object)
    build_dense_cloud = pg_step.BuildDenseCloud(workflow_object)
    # build_mesh = pg_step.BuildMesh(workflow_object)
    merge_chunks = pg_step.MergeChunks(workflow_object)
    # build_texture = pg_step.BuildTexture(workflow_object)
    build_DEM = pg_step.BuildDEM(workflow_object)

    # build_contours = pg_step.BuildContours(workflow_object)

    build_orthomosaic = pg_step.BuildOrthomosaic(workflow_object)
    create_shape = pg_step.CreateShape(workflow_object)

    # build_tiled_model = pg_step.BuildTiledModel(workflow_object)
    generate_report = pg_step.GenerateReport(workflow_object)

    wg = WorkflowGraph('Default Photogrammetry Workflow')
    print(wg)
    #wg.add_workflow_step(extract_video_frames)
    wg.add_workflow_step(add_photos)
    wg.add_workflow_step(check_camera_altitude)
    wg.add_workflow_step(estimate_image_quality)
    wg.add_workflow_step(align_photos)
    wg.add_workflow_step(addGCPs)
    # wg.add_workflow_step(detect_markers)
    # wg.add_workflow_step(check_marker_error)
    wg.add_workflow_step(optimize_camera)
    wg.add_workflow_step(bounding_box)
    wg.add_workflow_step(split_into_chunk)
    wg.add_workflow_step(build_dense_cloud)
    # wg.add_workflow_step(build_mesh)
    wg.add_workflow_step(merge_chunks)
    # wg.add_workflow_step(build_texture)
    wg.add_workflow_step(build_DEM)
    # wg.add_workflow_step(build_contours)
    wg.add_workflow_step(build_orthomosaic)
    wg.add_workflow_step(create_shape)
    # wg.add_workflow_step(build_tiled_model)
    wg.add_workflow_step(generate_report)

    # Connecting different steps together
    #wg.add_next_step(extract_video_frames, add_photos)
    wg.add_next_step(add_photos, check_camera_altitude)
    wg.add_next_step(check_camera_altitude, estimate_image_quality)
    wg.add_next_step(estimate_image_quality,align_photos)
    wg.add_next_step(align_photos, addGCPs)
    # wg.add_next_step(addGCPs,detect_markers)
    # wg.add_next_step(detect_markers,check_marker_error)
    wg.add_next_step(addGCPs,optimize_camera)
    wg.add_next_step(optimize_camera,split_into_chunk)
    wg.add_next_step(split_into_chunk,bounding_box)
    wg.add_next_step(bounding_box,build_dense_cloud)
    wg.add_next_step(build_dense_cloud,merge_chunks)
    # wg.add_next_step(build_mesh,merge_chunks)
    wg.add_next_step(merge_chunks,build_DEM)
    # wg.add_next_step(build_texture,build_DEM)
    wg.add_next_step(build_DEM,build_orthomosaic)
    wg.add_next_step(build_orthomosaic,create_shape)
    # wg.add_next_step(build_orthomosaic,build_tiled_model)
    wg.add_next_step(create_shape,generate_report)
    return wg
