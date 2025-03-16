from typing import Any, Dict


class GlobalModelState:
    def __init__(self) -> None:
        # the attributes are being stored as a dictionary because I couldnt think of a better way to "Null" initialize them
        # also this kinda lets the object have a dynamic set of attributes
        # also makes for easier visualizations for the object, which will be
        # useful when building a more intuitive ui for them
        self.__attributes: Dict[str, Any] = {}

    def set_diamater(self, diam: int):
        self.__attributes["diameter"] = diam
        print(f"[LUIS] diamater set to {diam}")

    def set_chan_to_segment(self, chan: int):
        if chan < 0 or chan > 3:
            raise Exception("channel to segment is out of bounds")

        self.__attributes["channel_to_segment"] = chan
        print(f"[LUIS] channel to segment set to {chan}")

    def set_chan2(self, chan2: int):
        if chan2 < 0 or chan2 > 3:
            raise Exception("channel to segment is out of bounds")

        self.__attributes["channel_2"] = chan2
        print(f"[LUIS] channel 2 set to {chan2}")

    def set_use_gpu(self, use_gpu: bool):
        self.__attributes["use_gpu"] = use_gpu
        print(f"[LUIS] use_put set to {use_gpu}")

    def set_flow_threshold(self, threshold: float):
        # check ranges for this
        self.__attributes["flow_threshold"] = threshold
        print(f"[LUIS] flow threshold set to {threshold}")

    def set_cellprob_threshold(self, prob_thresh: float):
        # check ranges for this
        self.__attributes["cellprob_threshold"] = prob_thresh
        print(f"[LUIS] cellprob  threshold set to {prob_thresh}")

    def set_norm_percentiles(self, lower: float | None, upper: float | None):
        # also check ranges for this one, expecially since its setting a raneg
        # for percentiles

        if not lower and not upper:
            return

        if "norm_percentiles" not in self.__attributes:
            self.__attributes["norm_percentiles"] = {
                "lower": 1.0, "upper": 99.0}

        # HUGE SMELL, NEED TO ADD CHECK FOR BOUNDS OF LOWER AND HIGHER, AND THAT THEY DONT OVERLAP
        # WILL ADD THIS WHEN I IMPLEMENT THE PROPER SETTERS WITH DECORATORS FOR
        # ALL THE ATTRIBUTES
        if lower:
            self.__attributes["norm_percentiles"]["lower"] = lower
        if upper:
            self.__attributes["norm_percentiles"]["higher"] = upper

        print(f"[LUIS] norm percentiles set to {lower} - {upper}")

    def set_niter_dynamics(self, niter_dys: int | float):
        # idk if this is mean to be an int or a float
        # but again check ranges for this
        self.__attributes["niter_dynamics"] = niter_dys
        print(f"[LUIS] niter dynamics set to {niter_dys}")

    def set_selected_model(self, model):
        # check types
        # find ways to determine model id
        # we probably need a model class (maybe taken from the same cellpose model class?) to be able to load/store them for final pipeline use
        # models have a path
        # models seem to have something called "diam_labels" and "diam_mean"?
        # (find out what these are)

        # temporary solution
        self.__attributes["model"] = model

    def __bool__(self):
        # returns false if we currently dont have a model state
        # meaning that the biologist hasnt yet finalized what their final
        # pipeline stage will look like
        pass
