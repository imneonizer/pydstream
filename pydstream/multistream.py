import sys

class MultiStream:
    def cb_newpad(self, decodebin, decoder_src_pad, data):
        caps = decoder_src_pad.get_current_caps()
        gststruct = caps.get_structure(0)
        gstname = gststruct.get_name()
        source_bin = data
        features = caps.get_features(0)

        # Need to check if the pad created by the decodebin is for video and not
        # audio.
        # print("gstname =", gstname)
        if(gstname.find("video") != -1):
            # Link the decodebin pad only if decodebin has picked nvidia
            # decoder plugin nvdec_*. We do this by checking if the pad caps contain
            # NVMM memory features.
            # print("features =",features)
            if features.contains("memory:NVMM"):
                # Get the source bin ghost pad
                bin_ghost_pad = source_bin.get_static_pad("src")
                if not bin_ghost_pad.set_target(decoder_src_pad):
                    sys.stderr.write("Failed to link decoder src pad to source bin ghost pad\n")
            else:
                sys.stderr.write(" Error: Decodebin did not pick nvidia decoder plugin.\n")

    def decodebin_child_added(self, child_proxy, Object, name, user_data):
        print("Decodebin child added:", name)
        if(name.find("decodebin") != -1):
            Object.connect("child-added", self.decodebin_child_added, user_data)

    def create_source_bin(self, index, uri):
        bin_name = "source-bin-%02d" % index
        print("Creating source bin:", bin_name)

        # Create a source GstBin to abstract this bin's content from the rest of the
        # pipeline
        nbin = self.check(self.Gst.Bin.new(bin_name))

        # Source element for reading from the uri.
        # We will use decodebin and let it figure out the container format of the
        # stream and the codec and plug the appropriate demux and decode plugins.
        uri_decode_bin = self.check(self.Gst.ElementFactory.make("uridecodebin", "uri-decode-bin"))

        # We set the input uri to the source element
        uri_decode_bin.set_property("uri", uri)

        # Connect to the "pad-added" signal of the decodebin which generates a
        # callback once a new pad for raw data has beed created by the decodebin
        uri_decode_bin.connect("pad-added", self.cb_newpad, nbin)
        uri_decode_bin.connect("child-added", self.decodebin_child_added, nbin)

        # We need to create a ghost pad for the source bin which will act as a proxy
        # for the video decoder src pad. The ghost pad will not have a target right
        # now. Once the decode bin creates the video decoder and generates the
        # cb_newpad callback, we will set the ghost pad target to the video decoder
        # src pad.
        self.Gst.Bin.add(nbin, uri_decode_bin)
        bin_pad = nbin.add_pad(self.Gst.GhostPad.new_no_target("src", self.Gst.PadDirection.SRC))
        if not bin_pad:
            sys.stderr.write(" Failed to add ghost pad in source bin \n")
            return None
        return nbin
    
    def add_uri(self, uri):
        if isinstance(uri, str):
            uri = [uri]

        for i, uri_name in enumerate(uri):
            if uri_name.find("rtsp://") == 0:
                self.islive = True
            
            source_bin = self.check(self.create_source_bin(i, uri_name))
            self.add(source_bin, f"source_bin_{i}")
            padname = "sink_%u" % i
            sinkpad = self.check(self.streammux.get_request_pad(padname))
            srcpad = self.check(source_bin.get_static_pad("src"))
            srcpad.link(sinkpad)