import argparse
import copy
import json
from uuid import uuid4
from datetime import datetime
from stix2elevator.stix_stepper import step_bundle
from copy import deepcopy
from tabulate import tabulate
from dateutil.parser import isoparse


class STIXToCollection:
    @staticmethod
    def stix_to_collection(bundle, name="[PLACEHOLDER]", version="9.0"):
        working_bundle = copy.deepcopy(bundle)
        for obj in working_bundle["objects"]:  # check to see if this bundle already contains a collection
            if obj["type"] == 'x-mitre-collection':
                return bundle
        if bundle.get("spec_version", "") is "2.0":
            print("[NOTE] - version 2.0 spec detected. Forcibly upgrading the bundle to 2.1 to support collections.")
            working_bundle = step_bundle(working_bundle)
            working_bundle["spec_version"] = "2.1"
        if working_bundle.get("spec_version", "") is not "2.1":
            print(f"[ERROR] - version {working_bundle.get('spec_version', '[NOT FOUND]')} is not one of [2.0, 2.1]. "
                  f"This module only processes stix 2.0 and stix 2.1 bundles.")
        time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        raw_collection = dict(type="x-mitre-collection", id=f"x-mitre-collection--{uuid4()}", spec_version="2.1",
                              name=name, x_mitre_version=version,
                              description="[This collection was autogenerated by STIXToCollection, as part of "
                                          "mitreattack-python]",
                              created_by_ref="", created=time, modified=time, object_marking_refs=[],
                              x_mitre_contents=[])
        for obj in working_bundle['objects']:
            raw_collection['x_mitre_contents'].append(dict(object_ref=obj["id"], object_modified=obj["modified"]))
            if obj["object_marking_refs"] not in raw_collection["object_marking_refs"]:
                raw_collection["object_marking_refs"].append(obj["object_marking_refs"])
            if obj["created_by_ref"] is not raw_collection["created_by_ref"]:
                if raw_collection["created_by_ref"] is not "":
                    print(f"[NOTE] multiple 'created_by_ref' values detected. {raw_collection['created_by_ref']} (first "
                          f"encountered) will take precedence over {obj['created_by_ref']}")
                    continue
                raw_collection["created_by_ref"] = obj["created_by_ref"]

        working_bundle["objects"].insert(0, raw_collection)
        return working_bundle


def main():
    parser = argparse.ArgumentParser(
        description="Update a STIX 2.0 or 2.1 bundle to include a collections object referencing the contents of the "
                    "bundle."
    )
    parser.add_argument("-bundle",
                        type=str,
                        default="bundle.json",
                        help="the input bundle file"
                        )
    parser.add_argument("-output",
                        type=str,
                        default="bundle_out.json",
                        help="the output bundle file"
                        )
    parser.add_argument("-name",
                        type=str,
                        default="[PLACEHOLDER]",
                        help="the name for the generated collection object")
    parser.add_argument("-version",
                        type=str,
                        default="9.0",
                        help="the Att&ck version for the generated collection object")
    args = parser.parse_args()
    with open(args.index, "r") as f:
        bundle = json.load(f)
        with open(args.output, "w") as f2:
            f2.write(STIXToCollection.stix_to_collection(bundle))


if __name__ == "__main__":
    main()
